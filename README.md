# Breath-AI

**Generate research-backed breathing content with a consistent brand voice.**

Built for my mindfulness app, **JustBreatheBro** — Breath-AI turns peer-reviewed research into app-ready breathing exercises while maintaining a calm, approachable tone.

- **App Store:** [Download JustBreatheBro](https://apps.apple.com/us/app/justbreathebro/id6756590863)
- **GitHub:** [github.com/michael-d-abraham/JustBreatheBro](https://github.com/michael-d-abraham/JustBreatheBro)

---

## Why I built this

I needed a way to generate breathing exercise content that was both scientifically accurate and consistent with the calm, approachable voice of the app.

Breath-AI solves this by generating content exclusively from a curated library of peer-reviewed research while using a separate style retrieval system to maintain a consistent brand voice. Strict guardrails prevent the system from relying on internet searches or unsupported information, ensuring responses remain grounded, accurate, and on-brand.

---

## Highlights

- **Built a complete RAG system from scratch**
- **Created a dual-retrieval architecture** (content + style)
- **Implemented hallucination guardrails**
- **Designed a production content-generation workflow**
- **Built something used by a real mobile app**

---

## What you can do

- Generate **descriptions**, **step-by-step methods**, **benefits**, and **short summaries**
- Keep a **consistent brand voice** across every exercise
- **Adapt tone** for sleep, anxiety, pre-work, mid-day reset, and more
- Trust the output — facts come from **your PDFs**, not the model's imagination

A user asks a question → BreathBot returns structured content → ready for a mobile app screen:

![How Breath-AI works end-to-end — CLI query to structured app content](images/HowItsUsed.png)

*Example: "Give me the method for Deep Breathing" produces step-by-step instructions, tips, and app-ready sections (Summary, Benefits, Method).*

```bash
python run.py "How do I do 4-7-8 breathing?"
python run.py --chat
python run.py "Describe box breathing" --context sleep --energy very_gentle
```

---

## Get started

```bash
pip install -r requirements.txt
```

Create `.env`:

```
GEMINI_API_KEY=your_key_here
```

Build the knowledge base (once):

```bash
python ingest_exercises.py   # PDFs → papers/
python ingest_style.py       # voice examples → style/
```

### Tone control

Four CLI flags shape every response without changing the architecture:

| Flag | Options |
|------|---------|
| `--audience-level` | `beginner` · `intermediate` |
| `--length` | `short` · `medium` · `long` |
| `--energy` | `very_gentle` · `neutral` · `slightly_uplifting` |
| `--context` | `sleep` · `mid-day_reset` · `pre-work` · `anxiety_spike` · `general` |

![System rules and fine-tuning variables — audience, length, energy, context](images/FineTuning.png)

*Left: hard rules (source-only facts, warm tone, safety). Right: the four variables injected into the language agent prompt.*

---

## What was built

| Layer | Files | Purpose |
|-------|-------|---------|
| **CLI** | `run.py` | Entry point — single query or `--chat` mode |
| **Agents** | `agent.py` | Two-LLM pipeline, early-return guardrails, tone params |
| **Models** | `model_utils.py` | Gemini via OpenAI-compatible API |
| **Ingestion** | `ingest_exercises.py`, `ingest_style.py` | PDF + style → ChromaDB |
| **Extraction** | `scraper.py` | PDF text extraction, URL/PDF fetching support |
| **Retrieval** | `tools/vector_store.py` | ChromaDB retrievers (content + style) |
| **Tools** | `tools/retrieval_tool.py` | smolagents tools for document + style search |
| **Report** | `REPORT.html` | Full system write-up (architecture, evaluation, PEAS) |

---

## Data sources

### Content corpus — `papers/` (7 research PDFs)

Scientific literature on breathing techniques, ingested into ChromaDB collection `breathing_exercises`:

- Diaphragmatic & deep breathing studies
- Pain self-management research
- Frontiers in Psychology breathing research
- Additional peer-reviewed PDFs on breathwork

**Pipeline:** PDF → PyPDF extraction → 500-char chunks (100 overlap) → local embeddings → vector store

### Style corpus — `style/` (4 voice guides)

Brand voice examples ingested into collection `breath_style_guides`:

| File | Content type |
|------|--------------|
| `shortDescription.txt` | 6–12 word summaries |
| `description.txt` | 2–4 sentence explanations |
| `benefit.txt` | Benefit lists |
| `method.txt` | Step-by-step instructions |

Update voice by adding `.txt` files — no prompt rewrites required.

### Output format standards

Every response follows three golden example formats retrieved from the style corpus:

![Golden example format standards — Summary, Benefits, Method](images/GoldenExamples.png)

| Section | Rules |
|---------|-------|
| **Summary** | 2–4 sentences · warm & clear · simple physiology terms |
| **Benefits** | One sentence, list-style · stress → physical → cognitive order |
| **Method** | 3–5 sentences · step-by-step · gentle active verbs |

---

## Architecture

Two specialized LLMs with separate responsibilities — formal retrieval vs. natural language styling:

![Breath Bot architecture — dual LLM pipeline, knowledge base, and agent orchestration](images/Architecture.png)

| Component | Role |
|-----------|------|
| **Knowledge Base** | Academic PDFs chunked and embedded in ChromaDB |
| **Formal LLM** | Retrieves raw data, applies system rules, returns structured JSON |
| **Natural Language LLM** | Applies style, fine-tune variables, and golden examples |
| **Agent** | Orchestrates the flow between user, retrieval, and styling |
| **Breath App output** | Summary · Benefits · Method — production-ready sections |

**Key design choices:**
- **Dual RAG** — content (`breathing_exercises`) and style (`breath_style_guides`) in separate collections
- **Source grounding** — language model only sees formatted retrieval output, not raw PDFs
- **Early return** — `NO_RELEVANT_INFORMATION` sentinel stops the pipeline before styling
- **Local embeddings** — `sentence-transformers/all-MiniLM-L6-v2`, zero embedding API cost

---

## Technical stack

| Category | Technology | Role |
|----------|------------|------|
| **Language** | Python 3 | Core runtime |
| **Agent framework** | [smolagents](https://github.com/huggingface/smolagents) | Tool-calling agents (`ToolCallingAgent`) |
| **LLM** | Google Gemini 2.5 Flash Lite | Retrieval + language agents (OpenAI-compatible API) |
| **Vector DB** | ChromaDB | Persistent storage — two collections |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Local semantic search (no API cost) |
| **Chunking** | LangChain `RecursiveCharacterTextSplitter` | 500 chars, 100 overlap |
| **PDF parsing** | PyPDF | Text extraction from research papers |
| **Web scraping** | BeautifulSoup4 + Requests | Optional URL/PDF fetching (`scraper.py`) |
| **Config** | python-dotenv | API key management via `.env` |
| **Interface** | argparse CLI | Single query + interactive chat |

### Python dependencies

```
smolagents · chromadb · sentence-transformers · langchain-text-splitters
python-dotenv · beautifulsoup4 · requests · pypdf
```

---

## Agent pipeline

| Step | Agent | Tool | Output |
|------|-------|------|--------|
| 1 | Retrieval Agent | `retrieve_documents` | Structured facts from PDFs (top-k=4) |
| 2 | Guard check | — | Stop if no relevant content found |
| 3 | Language Agent | `retrieve_style` | On-brand copy using style examples (top-k=4) |

**Safety built in:**
- Facts must come from ingested PDFs only
- Hedged wellness language ("may help", "can support")
- No medical claims or invented techniques
- Explicit uncertainty when knowledge base has no match

---

## Project evolution

| Phase | Focus |
|-------|-------|
| **Week 1–2** | Single LLM + system prompts for style control |
| **Week 3** | Style RAG corpus, dual retrieval, tone parameters |
| **Week 4** | Two-LLM architecture — retrieval vs. language separation |

---

## Key concepts demonstrated

- Retrieval-Augmented Generation (RAG)
- Multi-agent orchestration
- Source-grounded content generation
- Vector search with ChromaDB
- Tool-calling agents
- Prompt and context engineering
- PDF ingestion and embedding pipelines

---

## Documentation

| Resource | Description |
|----------|-------------|
| [`REPORT.html`](REPORT.html) | Full technical report — architecture, PEAS framework, evaluation |

---

*Built for real content workflows — accurate, controllable, and maintainable.*
