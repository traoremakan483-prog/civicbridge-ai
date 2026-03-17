import streamlit as st


def render_trust_message() -> None:
    """Render the grounding trust badge below the title."""
    st.info(
        "🔒 This answer is based only on the uploaded official documents.",
        icon=None,
    )


def render_official_answer(answer: str) -> None:
    """
    Render the Official Answer section.

    Args:
        answer: The grounded answer string from the RAG pipeline.
    """
    st.markdown("### 📄 Official Answer")
    st.markdown(answer)


def render_simple_explanation(explanation: str) -> None:
    """
    Render the Simple Explanation section.

    Args:
        explanation: The plain-language rewrite from simplifier.py.
    """
    st.markdown("### 💬 Simple Explanation")
    st.markdown(explanation)


def render_action_steps(steps: list[str]) -> None:
    """
    Render the Action Steps section as a numbered list.

    Args:
        steps: List of actionable step strings from action_steps.py.
    """
    st.markdown("### ✅ Action Steps")
    if not steps:
        st.markdown("_No action steps could be extracted from this answer._")
        return
    for i, step in enumerate(steps, start=1):
        st.markdown(f"**{i}.** {step}")


def render_next_steps(next_steps: dict) -> None:
    """
    Render the "What Should I Do Next?" structured guide.

    Args:
        next_steps: Dict from next_steps.py with keys:
            who_can_apply, required_documents, step_by_step_process,
            estimated_processing_time, important_notes.
    """
    st.markdown("### 🗺️ What Should I Do Next?")
    fields = [
        ("👤 Who can apply", next_steps.get("who_can_apply")),
        ("📋 Required documents", next_steps.get("required_documents")),
        ("🔢 Step-by-step process", next_steps.get("step_by_step_process")),
        ("⏱️ Estimated processing time", next_steps.get("estimated_processing_time")),
        ("⚠️ Important notes", next_steps.get("important_notes")),
    ]
    for label, value in fields:
        st.markdown(f"**{label}**")
        st.markdown(value or "_Not specified in the document._")


def render_source_excerpts(source_documents: list) -> None:
    """
    Render the source excerpts used to generate the answer.

    Args:
        source_documents: List of LangChain Document objects returned by
                          the RAG pipeline.
    """
    st.markdown("### 🔍 Source / Evidence")
    if not source_documents:
        st.markdown("_No source excerpts available._")
        return
    for i, doc in enumerate(source_documents, start=1):
        page = doc.metadata.get("page", "?")
        with st.expander(f"Excerpt {i} — page {page}"):
            st.markdown(f"_{doc.page_content.strip()}_")


def render_translation_output(translated_blocks: dict) -> None:
    """
    Render translated versions of all output sections.

    Args:
        translated_blocks: Dict mapping section label (str) to
                           translated text (str).
    """
    st.markdown("### 🌐 Translation")
    for label, text in translated_blocks.items():
        st.markdown(f"**{label}**")
        st.markdown(text)
        st.markdown("---")
