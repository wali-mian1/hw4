from __future__ import annotations

import asyncio
import json
import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, model_validator

try:
    from .audit import audit_event
    from .agent import shop_agent
    from .models import AgentDeps, ChatHistoryItem, ChatReply, ChatRequest
    from .tools import get_product as agent_get_product
except ImportError:  # Supports `uvicorn main:app` when launched from backend/.
    from audit import audit_event
    from agent import shop_agent
    from models import AgentDeps, ChatHistoryItem, ChatReply, ChatRequest
    from tools import get_product as agent_get_product


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "campus_customs.db"
PRODUCTS = ROOT / "data"

app = FastAPI(title="Campus Customs API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory=PRODUCTS), name="images")
PASSWORD_ITERATIONS = 120_000
sessions: dict[str, int] = {}


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def public_user(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
    }


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(11)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, salt, expected_digest = stored_hash.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    actual_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS
    ).hex()
    return hmac.compare_digest(actual_digest, expected_digest)


def current_user(authorization: str | None = Header(default=None)) -> dict:
    user = authenticated_user(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="You must be logged in")
    return user


def authenticated_user(authorization: str | None) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    user_id = sessions.get(authorization.removeprefix("Bearer ").strip())
    if user_id is None:
        return None
    with connect() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return public_user(row)


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def parse_json_array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def product_from_row(row: sqlite3.Row, inventory: list[dict] | None = None) -> dict:
    product = dict(row)
    product["colors"] = parse_json_array(product["colors"])
    product["search_tags"] = parse_json_array(product["search_tags"])
    product["image_url"] = f"/images/{product['image_file_path']}"
    if inventory is not None:
        product["inventory"] = inventory
    return product


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/chat/history", response_model=list[ChatHistoryItem])
def chat_history(user: dict = Depends(current_user)) -> list[ChatHistoryItem]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 40",
            (user["id"],),
        ).fetchall()
    history = []
    for row in reversed(rows):
        try:
            products = json.loads(row["products_json"] or "[]")
        except json.JSONDecodeError:
            products = []
        history.append(ChatHistoryItem(role=row["role"], content=row["content"], products=products, created_at=row["created_at"]))
    return history


@app.post("/api/chat", response_model=ChatReply)
async def chat(payload: ChatRequest, authorization: str | None = Header(default=None)) -> ChatReply:
    audit_event("agent_loop_started", args={"message_length": len(payload.message), "has_product_context": bool(payload.current_product_id)})
    user = authenticated_user(authorization)
    current_product = agent_get_product(payload.current_product_id) if payload.current_product_id else None
    prior_history: list[ChatHistoryItem] = []
    if user:
        with connect() as connection:
            rows = connection.execute(
                "SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 16",
                (user["id"],),
            ).fetchall()
        for row in reversed(rows):
            try:
                products = json.loads(row["products_json"] or "[]")
            except json.JSONDecodeError:
                products = []
            prior_history.append(ChatHistoryItem(role=row["role"], content=row["content"], products=products, created_at=row["created_at"]))
        with connect() as connection:
            connection.execute(
                "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
                (user["id"], payload.message),
            )
    context = AgentDeps(
        user_name=user["name"] if user else None,
        user_email=user["email"] if user else None,
        current_product=current_product,
        recent_history=prior_history,
    )
    try:
        result = await asyncio.wait_for(shop_agent.run(payload.message, deps=context), timeout=45)
        reply = result.output
        audit_event("agent_loop_stopped", result={"reply_length": len(reply.reply), "product_count": len(reply.products)}, stop_reason="completed")
    except asyncio.TimeoutError:
        reply = ChatReply(reply="I’m taking a little longer than usual to check the collection. Please try that question again in a moment.")
        audit_event("agent_loop_stopped", result={"fallback": True}, stop_reason="timeout_45_seconds")
    except Exception:
        reply = ChatReply(reply="I’m having trouble reaching the collection right now. Please try again in a moment, or browse the Products page directly.")
        audit_event("agent_loop_stopped", result={"fallback": True}, stop_reason="provider_or_runtime_error")
    if user:
        products_json = json.dumps([product.model_dump() for product in reply.products])
        with connect() as connection:
            connection.execute(
                "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
                (user["id"], reply.reply, products_json),
            )
    return reply


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest) -> dict:
    email = str(payload.email).lower()
    first_name = payload.first_name.strip()
    last_name = payload.last_name.strip()
    if not first_name or not last_name:
        raise HTTPException(status_code=422, detail="First and last name are required")
    with connect() as connection:
        existing = connection.execute("SELECT id FROM users WHERE lower(email) = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with that email already exists")
        cursor = connection.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (f"{first_name} {last_name}", email, hash_password(payload.password), first_name, last_name),
        )
        row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    token = secrets.token_urlsafe(32)
    sessions[token] = row["id"]
    return {"token": token, "user": public_user(row)}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict:
    email = str(payload.email).lower()
    with connect() as connection:
        row = connection.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = secrets.token_urlsafe(32)
    sessions[token] = row["id"]
    return {"token": token, "user": public_user(row)}


@app.get("/api/auth/me")
def me(user: dict = Depends(current_user)) -> dict:
    return user


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if authorization and authorization.startswith("Bearer "):
        sessions.pop(authorization.removeprefix("Bearer ").strip(), None)
    return {"status": "signed_out"}


@app.get("/api/products")
def list_products() -> list[dict]:
    with connect() as connection:
        rows = connection.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    return [product_from_row(row) for row in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory_rows = connection.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size",
            (product_id,),
        ).fetchall()
    inventory = [dict(item) for item in inventory_rows]
    return product_from_row(row, inventory)
