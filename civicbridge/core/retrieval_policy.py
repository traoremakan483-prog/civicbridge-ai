"""
Decide whether retrieved passages are actually relevant enough to answer from.

WHY THIS FILE EXISTS
────────────────────────────────────────────────────────────────────────────
The retriever used to be built with `search_type="similarity"` and `k=4`. A
similarity search always returns the k nearest passages — it has no notion of
"nothing here matches". Ask a healthcare knowledge base how to bake a cake and
it returns the four least-unrelated paragraphs, and the model answers from them.

That also made the guard in `rag_pipeline.generate_answer` unreachable:

    if not source_documents:            # never true when the index is non-empty
        return {"answer": "No relevant information was found ..."}

For a public-service assistant, refusing a question is not a degraded mode —
it is the single most important behaviour. Someone acting on a confidently
invented answer takes a day off work and shows up at the wrong counter with
the wrong papers.

This module holds only the DECISION, deliberately free of LangChain and FAISS,
so the rule can be tested without an API key, without embeddings, and without
network access. The plumbing lives in `vector_store.retrieve_relevant`.
"""

from dataclasses import dataclass

# ── Thresholds ──────────────────────────────────────────────────────────────
#
# Scores here are RELEVANCE scores in [0, 1] — higher is closer — as returned
# by LangChain's `similarity_search_with_relevance_scores`. They are NOT raw
# FAISS distances, where lower means closer. Mixing the two silently inverts
# the whole policy, so the conversion is done in one place and only there.
#
# MIN_RELEVANCE is a starting point, not a tuned constant. Calibrate it with
# `scripts/eval_retrieval.py` against the question set: too low lets unrelated
# questions through, too high makes the assistant refuse legitimate ones. The
# second failure is annoying; the first is dangerous. When in doubt, go higher.
MIN_RELEVANCE = 0.35

# Below this many passages clearing the bar, we treat the evidence as too thin
# to build an answer on, even if one passage scored well. One lucky paragraph
# match is usually a shared word, not a shared subject.
MIN_PASSAGES = 1


@dataclass(frozen=True)
class ScoredPassage:
    """A retrieved passage and how relevant it was judged to be."""

    text: str
    relevance: float
    metadata: dict | None = None


@dataclass(frozen=True)
class RetrievalDecision:
    """
    What the policy concluded, and why.

    `reason` is meant to be shown to a developer (logs, evaluation runs), never
    to a citizen — the user-facing wording lives in the UI labels.
    """

    passages: list[ScoredPassage]
    accepted: bool
    reason: str
    best_relevance: float


def decide(
    scored: list[ScoredPassage],
    min_relevance: float = MIN_RELEVANCE,
    min_passages: int = MIN_PASSAGES,
) -> RetrievalDecision:
    """
    Keep only passages that clear the relevance bar, and say whether what
    remains is enough to answer from.

    Args:
        scored:        Passages with relevance in [0, 1], any order.
        min_relevance: Bar a passage must clear to be used at all.
        min_passages:  How many must clear it before we agree to answer.

    Returns:
        A RetrievalDecision. When `accepted` is False the caller must NOT call
        the language model: there is nothing to ground an answer in, so any
        answer would be invention.
    """
    if not scored:
        return RetrievalDecision(
            passages=[],
            accepted=False,
            reason="the retriever returned nothing (empty or unbuilt index)",
            best_relevance=0.0,
        )

    for p in scored:
        if not 0.0 <= p.relevance <= 1.0:
            raise ValueError(
                f"relevance must be a normalised score in [0, 1], got {p.relevance!r}. "
                "A raw FAISS distance was probably passed instead of a relevance score — "
                "they are inverted, which would turn this policy upside down."
            )

    best = max(p.relevance for p in scored)
    kept = sorted(
        (p for p in scored if p.relevance >= min_relevance),
        key=lambda p: p.relevance,
        reverse=True,
    )

    if len(kept) < min_passages:
        return RetrievalDecision(
            passages=[],
            accepted=False,
            reason=(
                f"only {len(kept)} passage(s) reached {min_relevance:.2f}; "
                f"best was {best:.2f} — the question looks outside this document"
            ),
            best_relevance=best,
        )

    return RetrievalDecision(
        passages=kept,
        accepted=True,
        reason=f"{len(kept)} passage(s) at or above {min_relevance:.2f}, best {best:.2f}",
        best_relevance=best,
    )


def distance_to_relevance(distance: float) -> float:
    """
    Convert a FAISS L2 distance over normalised embeddings into a relevance
    score in [0, 1], the same way LangChain does.

    For unit-length vectors the L2 distance lies in [0, 2], so `1 - d / 2`
    maps identical vectors to 1.0 and opposite ones to 0.0. Exposed as a named
    function precisely because getting this inversion wrong is silent: the
    assistant would answer confidently on the LEAST relevant passages.
    """
    if distance < 0:
        raise ValueError(f"a distance cannot be negative, got {distance!r}")
    return max(0.0, min(1.0, 1.0 - distance / 2.0))
