from langchain_openai import ChatOpenAI

from config.prompts import TRANSLATE_TO_ENGLISH_PROMPT, TRANSLATION_PROMPT
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


def translate_to_english(question: str, source_language: str) -> str:
    """
    Translate a citizen's question from a supported language into English
    so it can be used for vector-store retrieval.

    If source_language is "English" the original question is returned unchanged.

    Args:
        question:        The question as typed by the user.
        source_language: Display name of the input language, e.g. "Malay".

    Returns:
        The question in English as a plain string.
    """
    if not question or not question.strip():
        raise ValueError("Cannot translate an empty question.")

    if source_language == "English":
        return question.strip()

    prompt = TRANSLATE_TO_ENGLISH_PROMPT.format(
        source_language=source_language,
        question=question,
    )

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)
    return response.content.strip()
