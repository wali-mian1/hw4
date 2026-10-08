from __future__ import annotations

import os
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from .models import AgentDeps, ChatReply
    from .tools import get_product, lookup_product_info, lookup_stock, search_catalogue
except ImportError:  # Supports `uvicorn main:app` when launched from backend/.
    from models import AgentDeps, ChatReply
    from tools import get_product, lookup_product_info, lookup_stock, search_catalogue


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_CANDIDATES = [PROJECT_ROOT / ".env", PROJECT_ROOT.parents[2] / ".env", PROJECT_ROOT.parents[3] / ".env"]


def load_env() -> None:
    for env_path in ENV_CANDIDATES:
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        if os.environ.get("PORTKEY_API_KEY"):
            break


load_env()
portkey_client = AsyncOpenAI(
    api_key=os.environ.get("PORTKEY_API_KEY", ""),
    base_url="https://api.portkey.ai/v1",
)
model = OpenAIResponsesModel("gpt-5.6-luna", provider=OpenAIProvider(openai_client=portkey_client))
system_prompt = (Path(__file__).parent / "prompts" / "prompt.md").read_text()

shop_agent = Agent(
    model,
    name="campus_customs_agent",
    output_type=ChatReply,
    deps_type=AgentDeps,
    system_prompt=system_prompt,
    tools=[search_catalogue, get_product, lookup_product_info, lookup_stock],
    retries=2,
)


@shop_agent.instructions
def add_shopper_context(ctx: RunContext[AgentDeps]) -> str:
    deps = ctx.deps
    identity = "The shopper is a guest. Do not imply you know their identity."
    if deps.user_name or deps.user_email:
        identity = f"The authenticated shopper is {deps.user_name or 'a shopper'} ({deps.user_email or 'email unavailable'})."
    page = "No product detail page is currently active."
    if deps.current_product:
        product = deps.current_product
        page = f"The shopper is currently viewing {product.name} (product_id={product.product_id}), priced at ${product.price:.2f}. Use this as the meaning of 'this item' or 'this' unless the shopper clearly names another product."
    history = ""
    if deps.recent_history:
        lines = [f"{item.role}: {item.content}" for item in deps.recent_history[-8:]]
        history = " Recent saved conversation context:\n" + "\n".join(lines)
    return f"{identity} {page}{history}"
