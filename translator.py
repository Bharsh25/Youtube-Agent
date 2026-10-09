"""Translate the video analysis into other languages using one agent per language."""

from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent

from agno.agent import Agent
from agno.models.groq import Groq

from youtube_analyzer import MODEL_ID

SUPPORTED_LANGUAGES = ["Hindi", "Marathi"]


def build_translator(language: str, api_key: str | None = None) -> Agent:
    """Create an agent that translates Markdown analysis into one language."""
    return Agent(
        name=f"{language} Translator",
        role=f"Translates video analyses into {language}",
        model=Groq(id=MODEL_ID, api_key=api_key),
        instructions=dedent(f"""\
            You are a professional translator. Translate the user's Markdown
            document into natural, fluent {language}.

            Rules:
            - Preserve the Markdown structure exactly: headings, tables, bullets, bold, and emojis.
            - Keep every timestamp (mm:ss or h:mm:ss) unchanged.
            - Keep URLs, code, product names, and brand names in their original form.
            - Translate section headings and table headers too.
            - Return only the translated document, with no preamble or commentary.
        """),
        markdown=True,
    )


def translate_analysis(
    markdown_text: str,
    languages: list[str],
    api_key: str | None = None,
) -> dict[str, str]:
    """Translate the analysis into each requested language in parallel.

    Returns a dict like {"Hindi": "...", "Marathi": "..."}.
    """
    if not languages:
        return {}

    def run_one(language: str) -> tuple[str, str]:
        translator = build_translator(language, api_key)
        response = translator.run(
            f"Translate this document into {language}:\n\n{markdown_text}"
        )
        return language, response.content or ""

    with ThreadPoolExecutor(max_workers=len(languages)) as pool:
        return dict(pool.map(run_one, languages))
