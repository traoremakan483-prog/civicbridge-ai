import json

from langchain_openai import ChatOpenAI

from config.prompts import (
    BATCH_TRANSLATION_PROMPT,
    TRANSLATE_TO_ENGLISH_PROMPT,
)
from core.answer_schema import parse_translated_blocks
from config.settings import DEFAULT_LLM_MODEL, SUPPORTED_LANGUAGES



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


def translate_blocks(blocks: dict, target_language: str) -> dict:
    """
    Traduire tous les blocs en UN appel, au lieu d'un appel par bloc.

    L'ancienne version faisait une comprehension de dictionnaire sur
    translate_text() : jusqu'a huit allers-retours sequentiels pour une seule
    question, chacun avec sa latence complete.

    Si le modele omet un libelle ou renvoie du JSON invalide, on retombe sur
    l'anglais d'origine pour ce bloc. Montrer la source est une imperfection
    visible ; une section vide est une imperfection silencieuse, et le lecteur
    ne saurait jamais qu'un paragraphe a disparu.

    Args:
        blocks:          libelle -> texte anglais.
        target_language: langue cible, presente dans SUPPORTED_LANGUAGES.

    Returns:
        libelle -> texte traduit (ou anglais d'origine en cas d'echec).
    """
    if not blocks:
        return {}

    if target_language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        raise ValueError(
            f"Unsupported language: '{target_language}'. Supported: {supported}."
        )

    if target_language == "English":
        return dict(blocks)

    payload = json.dumps(blocks, ensure_ascii=False, indent=2)
    prompt = BATCH_TRANSLATION_PROMPT.format(
        target_language=target_language,
        payload=payload,
    )

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    return parse_translated_blocks(llm.invoke(prompt).content, blocks)
