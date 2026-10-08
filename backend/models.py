from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class ProductCard(BaseModel):
    product_id: str
    name: str
    garment_type: str
    price: float
    description: str
    image_url: str
    colors: list[str] = Field(default_factory=list)
    available_sizes: list[str] = Field(default_factory=list)
    total_stock: int = 0


class ProductInfo(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    colors: list[str] = Field(default_factory=list)
    image_url: str


class StockLine(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class StockResult(BaseModel):
    product_id: str
    product_name: str
    requested_size: str | None = None
    stock: list[StockLine] = Field(default_factory=list)
    total_stock: int = 0


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    current_product_id: str | None = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)


@dataclass
class AgentDeps:
    user_name: str | None = None
    user_email: str | None = None
    current_product: ProductCard | None = None
    recent_history: list[ChatHistoryItem] = field(default_factory=list)
