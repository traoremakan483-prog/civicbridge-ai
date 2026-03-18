import html

import streamlit as st


def _safe_html(text: str) -> str:
    """Escape HTML special characters and convert newlines to <br> tags."""
    return html.escape(str(text)).replace("\n", "<br>")


def _card(title: str, body_html: str, variant: str = "") -> None:
    """
    Render a styled card block with a title and HTML body.

    Args:
        title:     Section title string (rendered as a label above the body).
        body_html: Inner HTML content for the card body.
        variant:   CSS class suffix for colour accent (e.g. "answer", "simple").
    """
    st.markdown(
        f'<div class="cb-card cb-{variant}"><div class="cb-card-label">{title}</div><div class="cb-card-body">{body_html}</div></div>',
        unsafe_allow_html=True,
    )


def render_trust_message() -> None:
    """Render the grounding trust badge."""
    st.markdown(
        """
        <div class="cb-card cb-trust">
            <span class="cb-trust-icon">🔒</span>
            <span class="cb-trust-text">
                This answer is based <strong>only</strong> on the uploaded official documents.
                No external knowledge has been used.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_official_answer(answer: str) -> None:
    """
    Render the Official Answer section.

    Args:
        answer: The grounded answer string from the RAG pipeline.
    """
    _card(
        "📄 Official Answer",
        f"<p>{_safe_html(answer)}</p>",
        "answer",
    )


def render_simple_explanation(explanation: str) -> None:
    """
    Render the Simple Explanation section.

    Args:
        explanation: The plain-language rewrite from simplifier.py.
    """
    _card(
        "💬 Simple Explanation",
        f"<p>{_safe_html(explanation)}</p>",
        "simple",
    )


def render_action_steps(steps: list[str]) -> None:
    """
    Render the Action Steps section as a numbered list.

    Args:
        steps: List of actionable step strings from action_steps.py.
    """
    if not steps:
        body = '<p><em>No action steps could be extracted from this answer.</em></p>'
    else:
        items = "".join(
            f'<div class="cb-step-row"><span class="cb-step-num">{i}</span><span class="cb-step-text">{_safe_html(step)}</span></div>'
            for i, step in enumerate(steps, start=1)
        )
        body = f'<div class="cb-step-list">{items}</div>'

    st.markdown(
        f'<div class="cb-card cb-steps"><div class="cb-card-label">✅ Action Steps</div><div class="cb-card-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def render_next_steps(next_steps: dict) -> None:
    """
    Render the "What Should I Do Next?" structured guide.

    Args:
        next_steps: Dict from next_steps.py with keys:
            who_can_apply, required_documents, step_by_step_process,
            estimated_processing_time, important_notes.
    """
    fields = [
        ("👤 Who can apply", next_steps.get("who_can_apply")),
        ("📋 Required documents", next_steps.get("required_documents")),
        ("🔢 Step-by-step process", next_steps.get("step_by_step_process")),
        ("⏱ Estimated processing time", next_steps.get("estimated_processing_time")),
        ("⚠️ Important notes", next_steps.get("important_notes")),
    ]
    rows = "".join(
        f'<div class="cb-field-row"><div class="cb-field-label">{label}</div><div class="cb-field-value">{_safe_html(value) if value else "<em>Not specified in the document.</em>"}</div></div>'
        for label, value in fields
    )
    _card("🗺️ What Should I Do Next?", rows, "next")


def render_source_excerpts(source_documents: list) -> None:
    """
    Render the source excerpts used to generate the answer.

    Args:
        source_documents: List of LangChain Document objects returned by
                          the RAG pipeline.
    """
    st.markdown(
        '<div class="cb-section-label">🔍 Source / Evidence</div>',
        unsafe_allow_html=True,
    )
    if not source_documents:
        st.markdown("_No source excerpts available._")
        return
    for i, doc in enumerate(source_documents, start=1):
        page = doc.metadata.get("page", "?")
        source = doc.metadata.get("source", "document")
        label = f"Excerpt {i} · page {page}"
        with st.expander(label):
            st.caption(f"Source: {source}  ·  Page {page}")
            st.markdown(
                f'<div class="cb-excerpt-text">{_safe_html(doc.page_content.strip())}</div>',
                unsafe_allow_html=True,
            )


def render_translation_output(translated_blocks: dict, language: str = "") -> None:
    """
    Render translated versions of all output sections.

    Args:
        translated_blocks: Dict mapping section label (str) to translated text (str).
        language:          Display name of the target language.
    """
    title = f"🌐 Translation — {language}" if language else "🌐 Translation"
    rows = "".join(
        f'<div class="cb-field-row"><div class="cb-field-label">{html.escape(label)}</div><div class="cb-field-value">{_safe_html(text)}</div></div>'
        for label, text in translated_blocks.items()
    )
    _card(title, rows, "translate")
