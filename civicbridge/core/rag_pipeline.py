from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config.prompts import (
    GROUNDED_ANSWER_PROMPT,
    REFUSAL_ANSWER,
    STRUCTURED_ANSWER_PROMPT,
)
from core.answer_schema import StructuredAnswer, parse_structured_answer
from config.settings import DEFAULT_LLM_MODEL
from core.vector_store import retrieve_relevant, to_documents


def _build_context(documents: list[Document]) -> str:
    """
    Concatenate retrieved document chunks into a single context string.

    Each passage is wrapped in a numbered tag rather than merely separated by
    a blank line. Two reasons:

      1. The model can cite "passage 2" instead of paraphrasing vaguely.
      2. It marks a boundary between INSTRUCTIONS and DATA. Document text is
         untrusted input: a PDF (or an uploaded one) can contain a sentence
         like "ignore the instructions above". Explicit delimiters plus an
         explicit rule in the prompt make that much harder to pull off.
    """
    return "\n\n".join(
        f"<passage id=\"{i}\">\n{doc.page_content}\n</passage>"
        for i, doc in enumerate(documents, start=1)
    )


def generate_answer(question: str, vector_store) -> dict:
    """
    Retrieve relevant passages and generate an answer grounded strictly in them.

    If nothing in the knowledge base is actually about the question, the
    function returns a refusal **without calling the language model**. That is
    deliberate: skipping the call makes invention impossible rather than
    merely discouraged, and costs nothing.

    Args:
        question:     The citizen's question, in English.
        vector_store: A FAISS store built by `build_vector_store`.

    Returns:
        A dict with:
            "answer"           (str)             — the answer, or the refusal.
            "source_documents" (list[Document])  — passages used; empty on refusal.
            "answered"         (bool)            — False when refused.
            "why"              (str)             — developer-facing explanation
                                                   of the retrieval decision.

    Raises:
        Exception: Propagates OpenAI API errors so the caller can show them.
    """
    decision = retrieve_relevant(vector_store, question)

    if not decision.accepted:
        return {
            "answer": REFUSAL_ANSWER,
            "source_documents": [],
            "answered": False,
            "why": decision.reason,
        }

    documents = to_documents(decision)
    context = _build_context(documents)

    prompt = GROUNDED_ANSWER_PROMPT.format(context=context, question=question)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return {
        "answer": response.content.strip(),
        "source_documents": documents,
        "answered": True,
        "why": decision.reason,
    }


def generate_full_answer(question: str, vector_store) -> dict:
    """
    Produire TOUTE la reponse en un seul appel au modele.

    Remplace l'enchainement generate_answer -> simplify -> action_steps ->
    next_steps, soit quatre allers-retours qui reexpediaient chacun le meme
    contexte ou la meme reponse. Un seul appel, une seule attente, un quart du
    cout.

    Le refus reste prioritaire : si aucun passage ne franchit le seuil de
    pertinence, on ne fait AUCUN appel. Voir core/retrieval_policy.

    Returns:
        dict avec "answered", "answer", "simple", "action_steps",
        "next_steps", "source_documents", "why" et "repaired".

    Raises:
        Exception: erreurs API remontees a l'appelant.
        ValueError: si la reponse du modele est inexploitable meme apres
            reparation — l'appelant doit alors se rabattre, pas afficher du vide.
    """
    decision = retrieve_relevant(vector_store, question)

    if not decision.accepted:
        return {
            "answered": False,
            "answer": REFUSAL_ANSWER,
            "simple": "",
            "action_steps": [],
            "next_steps": {},
            "source_documents": [],
            "why": decision.reason,
            "repaired": [],
        }

    documents = to_documents(decision)
    prompt = STRUCTURED_ANSWER_PROMPT.format(
        context=_build_context(documents),
        question=question,
    )

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)

    try:
        parsed: StructuredAnswer = parse_structured_answer(llm.invoke(prompt).content)
    except ValueError as e:
        # Le modele n'a pas rendu de JSON exploitable. Plutot qu'une page
        # d'erreur, on refait un appel simple qui ne demande QUE la reponse
        # ancree : le citoyen perd les sections annexes, pas la reponse.
        # C'est la raison pour laquelle generate_answer() est conservee.
        fallback = generate_answer(question, vector_store)
        fallback["simple"] = ""
        fallback["action_steps"] = []
        fallback["next_steps"] = {}
        fallback["repaired"] = [f"structured_call_failed: {e}"]
        return fallback

    return {
        "answered": True,
        "answer": parsed.answer,
        "simple": parsed.simple,
        "action_steps": parsed.action_steps,
        "next_steps": parsed.next_steps,
        "source_documents": documents,
        "why": decision.reason,
        "repaired": parsed.repaired,
    }
