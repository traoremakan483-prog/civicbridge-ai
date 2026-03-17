from langchain_openai import ChatOpenAI

from config.prompts import TRANSLATION_PROMPT
from config.settings import DEFAULT_LLM_MODEL, SUPPORTED_LANGUAGES


def translate_text(text: str, target_language: str) -> str:
    """
    Translate a block of text into one of the supported languages.

    The translation preserves meaning, tone, and formatting (numbered
    lists, bullet points). Only languages defined in SUPPORTED_LANGUAGES
    in config/settings.py are accepted.

    Args:
        text:            The text to translate.
        target_language: Display name of the target language, e.g. "Malay"
                         or "Indonesian". Must match a key in SUPPORTED_LANGUAGES.

    Returns:
        The translated text as a plain string.

    Raises:
        ValueError: If target_language is not in SUPPORTED_LANGUAGES,
                    or if the input text is empty.
        Exception: Propagates any OpenAI API errors to the caller.
    """
    if not text or not text.strip():
        raise ValueError("Cannot translate empty text.")

    if target_language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        raise ValueError(
            f"Unsupported language: '{target_language}'. "
            f"Supported languages are: {supported}."
        )

    prompt = TRANSLATION_PROMPT.format(
        target_language=target_language,
        text=text,
    )

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return response.content.strip()
