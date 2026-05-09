"""LLM service — turns a questionnaire submission into a DesignBrief."""

from __future__ import annotations

import json
import re
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.prompts import HUMAN_PROMPT, SYSTEM_PROMPT, build_product_prompt
from app.schemas import DesignBrief, QuestionnaireSubmission, StoneSuitability

logger = get_logger(__name__)

_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

_JSON_FENCE_RE = re.compile(r"```(?:json)?", re.IGNORECASE)


def _build_chain():
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        temperature=settings.llm_temperature,
    )
    return _CHAT_PROMPT | llm | StrOutputParser()


def _parse_response(raw: str) -> DesignBrief:
    cleaned = _JSON_FENCE_RE.sub("", raw).strip().rstrip("`").strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned non-JSON response: %s", cleaned[:300])
        raise ValueError("LLM response was not valid JSON.") from exc

    image_prompt = data.get("image_prompt")
    if not image_prompt or not isinstance(image_prompt, str):
        raise ValueError("LLM response is missing 'image_prompt'.")

    return DesignBrief(image_prompt=image_prompt, cautions=data.get("cautions"))


async def generate_design_brief(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> DesignBrief:
    """Build a structured product brief and return the LLM-generated DesignBrief."""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")

    product_prompt = build_product_prompt(submission, stone_assessment)
    chain = _build_chain()
    raw = await chain.ainvoke({"product_prompt": product_prompt})
    return _parse_response(raw)
