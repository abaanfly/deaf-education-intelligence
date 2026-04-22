"""Claude Sonnet 4.5 chat helper (via Emergent Universal Key)."""
from __future__ import annotations
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage
from core.db import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)


async def llm_chat(session_id: str, system_message: str, user_text: str) -> str:
    if not EMERGENT_LLM_KEY:
        return "(AI unavailable — missing LLM key.)"
    try:
        chat = (
            LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=session_id,
                system_message=system_message,
            )
            .with_model("anthropic", "claude-sonnet-4-5-20250929")
        )
        return await chat.send_message(UserMessage(text=user_text))
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM error")
        return f"(AI temporarily unavailable: {exc})"
