# 🌏 CivicBridge — Multilingual Public Service Navigator

CivicBridge is a multilingual AI-powered assistant that helps citizens understand
public-service support across healthcare, social aid, emergency relief, and family care.
Built for a 2-day hackathon, it is a fully functional RAG-based prototype with multilingual
input/output support.

The **primary experience** is built around four built-in support domains backed by curated
official-style prototype source guides. Users can also upload their own PDF as an optional
advanced mode.

---

## What CivicBridge Does

Citizens select a support domain, ask a question in English, Malay, or Indonesian, and receive:

- A **grounded official answer** based strictly on the selected knowledge base
- A **plain-language explanation** of the official answer
- **Action steps** — numbered, concrete tasks the citizen should take
- A **What Should I Do Next** guide covering eligibility, documents, process, and timeline
- **Source excerpts** showing exactly which parts of the document were used
- A **full translation** of all outputs into the user's chosen language

All answers are grounded in the built-in curated source documents.
No external web search or live government API is used.

---

## Built-In Support Domains

CivicBridge ships with four curated official-style prototype source guides:

| Domain | Program | Source File |
|--------|---------|-------------|
| 🏥 Healthcare Support | National Healthcare Assistance Program (NHAP) | `NHAP_Official_Guide.pdf` |
| 🤝 Social Support | Community Social Support Grant (CSSG) | `CSSG_Official_Guide.pdf` |
| 🚑 Emergency Medical Relief | Emergency Medical Relief Program (EMRP) | `EMRP_Official_Guide.pdf` |
| 👨‍👩‍👧 Family Care Support | Family Care Support Allowance (FCSA) | `FCSA_Official_Guide.pdf` |

Each guide covers program overview, eligibility criteria, required documents,
application steps, processing time, and important conditions.

> **Honesty note:** These are curated official-style prototype guides created for
> hackathon demonstration purposes. They are **not** live government web sources,
> and CivicBridge does **not** perform live web retrieval or query any government API.
> Answers are strictly grounded in the bundled PDF content.

---

## Optional: Custom Document Upload

Users can upload their own official PDF under the **Advanced: Custom Document** expander
in the sidebar. This temporarily overrides the selected built-in domain for that session.
The upload is optional and secondary to the built-in domain experience.

---

## Multilingual Support

| Feature | Languages |
|---------|-----------|
| Question input and answers | English, Malay, Tamil, Mandarin, Bengali, Nepali, Burmese, Indonesian |
| Interface labels | English, Malay, Indonesian — other languages fall back to English |

The first version offered English, Malay and Indonesian. A hackathon judge pointed out
that this was thin *given the concept itself*, and they were right — twice over.

Malay and Indonesian are largely mutually intelligible, so three entries in the dropdown
were really **two** reaches. Worse, they were the wrong three. Malaysian public services
already publish in Malay and English: the people those two languages cover were mostly
managing already. The people who are not are migrant workers — Bengali, Nepali, Burmese —
Tamil-speaking Malaysian Indians, and older Mandarin speakers.

Nothing technical was stopping this. Translation goes through the model, so a language is
one line in `config/settings.py`. It was a product failure, not an engineering one: the
languages picked were the ones the author knew, not the ones the users needed.

**Translations are shown next to the English source.** Machine-translating official
guidance into a low-resource language is not a neutral act — an error sends someone to the
wrong office with the wrong documents, after taking a day off they could not afford. The
answer is not to refuse to translate, but to make checking possible: a bilingual relative
or a counter clerk can compare the two columns before the person travels.

---

## Cost per question

Answering one question used to take up to thirteen sequential round-trips to the model:
translate the question, generate the answer, simplify it, extract action steps, build the
"what next" guide, then translate each of the eight output sections separately. Every one
of those calls re-sent the same passages or the same answer over the wire.

The four generation calls are now **one** call returning JSON, and the eight translation
calls are **one** call translating the whole payload.

| | before | after |
|---|---|---|
| Question in English | 4 | 1 |
| Question in another language, translated back | 13 | 3 |

The price of that is a new failure mode — a model can return malformed JSON, drop a key,
or wrap the object in a code fence. So the response is parsed as untrusted input in
`civicbridge/core/answer_schema.py`, missing sections are repaired rather than left blank,
and if the JSON is unusable at all the app falls back to a plain grounded answer instead of
showing an error. That parser is covered by 17 tests that run without an API key.

---

## Answering, and refusing

The retriever used to be a plain similarity search with `k=4`. A similarity search always
returns its four nearest neighbours — it cannot express *nothing here matches*. Ask a
healthcare knowledge base how to bake a cake and it returned four weakly-related paragraphs
and answered from them. The guard meant to catch this was unreachable code.

Retrieved passages now have to clear a relevance threshold before they are used at all, and
when none does, **the refusal is returned without calling the model**: skipping the call
makes invention impossible rather than merely discouraged, and costs nothing.

That decision lives in `civicbridge/core/retrieval_policy.py`, deliberately free of
LangChain and FAISS, so it can be tested without an API key — see below.

---

---

## Architecture

```
User question (any language)
        │
        ▼
[Input translation → English]   ← skipped if already English
        │
        ▼
[FAISS vector store retrieval]  ← top-K relevant chunks from selected PDF
        │
        ▼
[Grounded answer generation]    ← GPT-4o-mini, context-only, no hallucination
        │
        ├─► [Plain-language simplification]
        ├─► [Action steps extraction]
        └─► [Next steps guide]
                │
                ▼
        [Output translation]    ← on demand, user's chosen language
```

**Stack:**
- LLM: OpenAI GPT-4o-mini (via LangChain)
- Embeddings: OpenAI text-embedding-3-small
- Vector store: FAISS (in-memory, no persistence required)
- PDF parsing: PyMuPDF
- UI: Streamlit

---

## Getting Started
access with : https://public-service-ai.replit.app/
or

### 1. Clone the repository

```bash
git clone https://github.com/traoremakan483-prog/civicbridge-ai.git
cd civicbridge-ai
```

### 2. Install dependencies

```bash
pip install -r civicbridge/requirements.txt
```

### 3. Set your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the app

```bash
streamlit run civicbridge/app.py --server.port 5000
```

Open `http://localhost:5000` in your browser.

---

## Project Structure

```
civicbridge/
├── app.py                    # Main Streamlit application
├── requirements.txt
├── docs/
│   ├── NHAP_Official_Guide.pdf   # Healthcare Support
│   ├── CSSG_Official_Guide.pdf   # Social Support
│   ├── EMRP_Official_Guide.pdf   # Emergency Medical Relief
│   └── FCSA_Official_Guide.pdf   # Family Care Support
├── config/
│   ├── settings.py           # Domain map, language config, UI labels (i18n)
│   └── prompts.py            # All LLM prompt templates
├── core/
│   ├── document_loader.py    # PDF loading and text splitting
│   ├── vector_store.py       # FAISS index builder and retriever
│   ├── rag_pipeline.py       # Grounded answer generation
│   ├── simplifier.py         # Plain-language simplification
│   ├── action_steps.py       # Action steps extraction
│   ├── next_steps.py         # What Should I Do Next guide
│   └── translator.py         # Output translation + question→English
└── ui/
    └── components.py         # Streamlit rendering components
```

---

## Tests

```bash
python -m unittest discover -s tests -v
```

Standard library only — no OpenAI key, no embeddings, no network. That is the point of
keeping the retrieval decision separate from FAISS: the rule that decides whether
CivicBridge answers or refuses is checkable on every commit, in milliseconds.

The tests cover the behaviour the old code could not produce at all — refusing an
off-topic question, returning nothing to answer from, surviving an empty index — and the
inversion trap: FAISS returns *distance* (lower is closer) while the policy expects
*relevance* (higher is closer). Confusing the two raises nothing by itself; it just makes
the assistant answer from the least relevant passages. Passing a raw distance is rejected
loudly for that reason.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |

Do **not** commit `.env` to version control. It is listed in `.gitignore`.

---

## Future Improvements

The following are realistic next steps for a production version of CivicBridge:

- **More support domains** — expand to education, housing, employment, and legal aid
- **More languages and dialects** — add Tamil, Mandarin, and regional dialects
- **Real official-source integrations** — connect to live government portals and APIs
- **Voice input and accessibility** — support speech-to-text for non-literate users
- **Mobile-first version** — lightweight PWA or native mobile app
- **Persistent history** — allow users to revisit past questions across sessions
- **Feedback loop** — let users flag answers as helpful or incorrect to improve quality
- **Multi-document retrieval** — query across all domains simultaneously

---

## Hackathon Notes

- Built in 2 days as a civic-tech AI prototype
- Fully portable — no database, no login, no external services beyond OpenAI
- Designed for demonstration of grounded, multilingual public-service navigation
- Grounding is enforced at the prompt level — the LLM answers strictly from
  retrieved document context only, with no access to external knowledge
- `.env` is excluded from the repository; all secrets are managed locally
