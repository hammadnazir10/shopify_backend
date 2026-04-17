from __future__ import annotations

import json
import re
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings
from app.models import DesignBrief, QuestionnaireSubmission, StoneSuitability
from app.prompts import SYSTEM_PROMPT, HUMAN_PROMPT, build_product_prompt


_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])


def _build_chain():
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        temperature=0.7,
    )
    return _chat_prompt | llm | StrOutputParser()


def _parse_response(raw: str) -> DesignBrief:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    data = json.loads(cleaned)
    return DesignBrief(
        image_prompt=data["image_prompt"],
        cautions=data.get("cautions"),
    )


async def generate_design_brief(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> DesignBrief:
    """
    Builds a structured product prompt from questionnaire answers, sends it to
    OpenAI, and returns a DesignBrief with image_prompt and optional cautions.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")

    product_prompt = build_product_prompt(submission, stone_assessment)
    chain = _build_chain()
    raw = await chain.ainvoke({"product_prompt": product_prompt})
    return _parse_response(raw)
