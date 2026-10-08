"""Pydantic / PydanticAI structured types for the Campus Customs backend."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Accounts (Problem 4) ----------------------------------------------------


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class PublicUser(BaseModel):
    """The only user fields ever sent to the browser (never the password hash)."""

    id: int
    first_name: str
    last_name: str
    name: str
    email: str


# --- Chat (Problem 5) ----------------------------------------------------------


class ChatTurn(BaseModel):
    """One earlier message in the conversation, sent by the frontend for context."""

    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="The customer's new message.")
    history: list[ChatTurn] = Field(
        default_factory=list,
        max_length=20,
        description="Earlier turns, oldest first. Used for guests only; logged-in history is loaded from chat_messages.",
    )
    current_product_id: str | None = Field(
        default=None,
        max_length=200,
        description="product_id of the page the customer is viewing (#/product/<id>). Validated before use.",
    )
    history_after_id: int | None = Field(
        default=None,
        ge=0,
        description="Logged-in 'New chat' boundary: only saved messages with a larger id are used as context.",
    )


class ProductSummary(BaseModel):
    """What the search_products tool returns for each matching product (no price or stock yet)."""

    product_id: str = Field(description="Exact catalogue product_id; use it to refer to the product.")
    name: str
    garment_type: str
    colors: list[str]


class SearchResults(BaseModel):
    """search_products result (Problem 9): matches, or grounded suggestions when nothing matches."""

    query: str
    matches: list[ProductSummary]
    ignored_words: list[str] = Field(
        default_factory=list, description="Very common words (e.g. 'yale') that couldn't produce a match on their own."
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="When there are no matches: real garment types that exist in the catalogue, to suggest a broader search.",
    )


class ProductResolution(BaseModel):
    """resolve_product result (Problem 9): is a product reference unique, ambiguous or unknown?"""

    status: str = Field(description="'unique', 'ambiguous' or 'not_found'.")
    product: ProductSummary | None = Field(default=None, description="The single match when status is 'unique'.")
    candidates: list[ProductSummary] = Field(
        default_factory=list, description="The real products that fit when status is 'ambiguous'. Ask the customer to choose."
    )


class ProductDetails(BaseModel):
    """get_product_details result: the authoritative catalogue row for one product."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float = Field(description="Price in US dollars, exactly as stored in the catalogue table.")


class SizeStock(BaseModel):
    size: str = Field(description="Size label exactly as stored in inventory (XS, S, M, L, XL, XXL).")
    quantity: int = Field(description="Units in stock, exactly as stored in inventory.")
    in_stock: bool = Field(description="True when quantity > 0.")


class InventoryResult(BaseModel):
    """check_inventory result: stock for one size, or for every size when no size was given."""

    product_id: str
    name: str
    sizes: list[SizeStock]


class NotFound(BaseModel):
    """Returned instead of data when a product or size can't be found, so the agent can say so honestly."""

    error: str = Field(description="What could not be found.")
    valid_sizes: list[str] = Field(default_factory=list, description="Sizes that do exist, when the size was the problem.")


class ChatReply(BaseModel):
    """The agent's structured output."""

    reply: str = Field(description="The message shown to the customer (Markdown allowed).")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_ids (copied exactly from tool results) of products the reply recommends or discusses.",
    )


class ProductCard(BaseModel):
    """A product the frontend can show as a clickable card; built from the database, not by the model."""

    product_id: str
    name: str
    garment_type: str
    image: str
    price: float


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    current_product_id: str | None = Field(
        default=None, description="The page product the agent was told about (null if none or not a real product)."
    )
    saved: bool = Field(default=False, description="True when both messages were saved to the user's chat history.")
    last_message_id: int | None = Field(default=None, description="chat_messages id of the saved assistant reply.")


# --- Customer context & saved history (Problem 8) ----------------------------


class CurrentProduct(BaseModel):
    """A catalogue-validated product the customer is viewing."""

    product_id: str
    name: str


class ChatContext(BaseModel):
    """Per-request context given to the agent (PydanticAI deps). Never contains email, hashes or secrets."""

    logged_in: bool
    first_name: str | None = None
    current_product: CurrentProduct | None = None


class HistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[HistoryMessage]
