"""The Campus Customs chatbot: a PydanticAI agent using gpt-5.6-luna through Portkey.

The system prompt is loaded from prompts/prompt.md. The agent's tools live in
tools.py, and its structured output (models.ChatReply) is defined in models.py.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")  # keep the server log clean

from dotenv import load_dotenv  # noqa: E402
from openai import AsyncOpenAI  # noqa: E402
from pydantic_ai import Agent, RunContext, capture_run_messages  # noqa: E402
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart  # noqa: E402
from pydantic_ai.models import Model  # noqa: E402
from pydantic_ai.models.openai import OpenAIResponsesModel  # noqa: E402
from pydantic_ai.providers.openai import OpenAIProvider  # noqa: E402
from pydantic_ai.usage import RunUsage, UsageLimits  # noqa: E402

import tools  # noqa: E402
from models import ChatContext, ChatReply, ChatTurn  # noqa: E402

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
load_dotenv(HERE.parent / ".env")  # hw4/.env
load_dotenv(HERE.parent.parent / ".env")  # the shared AI Class/.env

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")

# Execution limits (enforced by PydanticAI on every run; exceeding one raises UsageLimitExceeded).
MAX_MODEL_REQUESTS = 8  # agent-loop iterations (model calls) per customer message
MAX_TOOL_CALLS = 12  # tool calls per customer message
OUTPUT_RETRIES = 1  # times the model may retry an invalid structured answer
MODEL_TIMEOUT_S = 60  # per model request
USAGE_LIMITS = UsageLimits(request_limit=MAX_MODEL_REQUESTS, tool_calls_limit=MAX_TOOL_CALLS)


def build_model() -> Model:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set (put it in a .env file).")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
        timeout=MODEL_TIMEOUT_S,
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))


def build_agent(model: Model | None = None) -> Agent[ChatContext, ChatReply]:
    agent = Agent(
        model or build_model(),
        deps_type=ChatContext,
        output_type=ChatReply,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=[tools.search_products, tools.resolve_product, tools.get_product_details, tools.check_inventory],
        retries=OUTPUT_RETRIES,
    )

    @agent.instructions
    def customer_context(ctx: RunContext[ChatContext]) -> str:
        """Per-request facts about the customer and the page they're on (validated in main.py)."""
        c = ctx.deps
        lines = ["## Current customer context"]
        if c.logged_in:
            lines.append(f"- The customer is logged in. Their first name is {c.first_name}.")
        else:
            lines.append("- The customer is a guest (not logged in).")
        if c.current_product:
            lines.append(
                f"- The customer is viewing the product page for **{c.current_product.name}** "
                f"(product_id `{c.current_product.product_id}`). Words like \"this\", \"it\" or "
                "\"this one\" refer to that product unless the customer clearly means something else. "
                "Still call get_product_details / check_inventory with that product_id for any price, "
                "description or stock facts."
            )
        else:
            lines.append("- The customer is not viewing a specific product page.")
        return "\n".join(lines)

    return agent


@lru_cache(maxsize=1)
def get_agent() -> Agent[ChatContext, ChatReply]:
    """Built on first use, so the server can start (and auth works) even without an API key."""
    return build_agent()


def to_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Earlier chat turns from the frontend, as PydanticAI message history."""
    history: list[ModelMessage] = []
    for t in turns:
        if t.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=t.content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=t.content)]))
    return history


class ChatRun:
    """The agent's answer plus what's needed for the audit trail."""

    def __init__(self, output: ChatReply | None, messages: list[ModelMessage], usage: RunUsage):
        self.output, self.messages, self.usage = output, messages, usage


async def chat(
    message: str,
    turns: list[ChatTurn],
    context: ChatContext,
    agent: Agent[ChatContext, ChatReply] | None = None,
    usage_limits: UsageLimits = USAGE_LIMITS,
) -> ChatRun:
    """Run the agent once, within the execution limits.

    On failure the exception is re-raised with `.chat_run` attached (messages so far), so the
    caller can still audit what happened before the error.
    """
    usage = RunUsage()
    history = to_history(turns)
    with capture_run_messages() as messages:
        try:
            result = await (agent or get_agent()).run(
                message, message_history=history, deps=context, usage_limits=usage_limits, usage=usage
            )
        except Exception as exc:
            exc.chat_run = ChatRun(None, list(messages)[len(history):], usage)  # type: ignore[attr-defined]
            raise
    return ChatRun(result.output, list(messages)[len(history):], usage)  # only this run's messages
