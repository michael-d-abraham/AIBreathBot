# Breathing Exercise Content Generator Agent

**Repository:** https://github.com/michael-d-abraham/AIBreathBot

---

## Problem & Solution

**Problem:**
- Need to write consistent, accurate breathing exercise content for mobile app
- Maintaining uniform tone and style across many exercises
- Ensuring accuracy while keeping content beginner-friendly

**Solution:**
- AI agent with RAG (Retrieval-Augmented Generation) architecture
- Processes local PDFs → vector database → retrieves relevant content
- Two-LLM pipeline: retrieval/formatting → language cleaning/styling
- Style corpus ensures consistent voice
- Source-grounded: only uses information from knowledge base

---

## PEAS Framework

| Component | Description |
|-----------|-------------|
| **Performance** | Accurate content, matches app theme, beginner-friendly, minimal editing needed |
| **Environment** | CLI interface, ChromaDB vector store, Gemini 2.5 Flash LLM, style corpus |
| **Actuators** | Content generation, semantic search, style application, session management |
| **Sensors** | User queries, semantic similarity search, document retrieval, style example retrieval |

---

## System Architecture

### Two-LLM Pipeline

```
User Query (CLI)
    ↓
┌─────────────────────────────┐
│ Retrieval Agent (LLM 1)     │
│ • retrieve_documents tool   │
│ • Formats raw info           │
│ • Returns "NO_RELEVANT_     │
│   INFORMATION" if empty     │
└─────────────────────────────┘
    ↓ (if info found)
┌─────────────────────────────┐
│ Language Model (LLM 2)      │
│ • retrieve_style tool        │
│ • Cleans & simplifies        │
│ • Applies Breath app voice   │
│ • Uses tone parameters       │
└─────────────────────────────┘
    ↓
Styled Response → User
```

### Key Components

**Retrieval Agent** (`_build_retrieval_agent()` in `agent.py`):
- Model: Gemini 2.5 Flash via `model_utils.google_build_reasoning_model()`
- Tool: `RetrieveDocumentsTool` → `ChromaRetriever` → `breathing_exercises` collection
- Output: Formatted plain text (overview/steps/benefits/notes)
- Error handling: Returns `"NO_RELEVANT_INFORMATION"` sentinel when no documents found

**Language Model** (`_build_language_model()` in `agent.py`):
- Model: Gemini 2.5 Flash (same as retrieval agent)
- Tool: `RetrieveStyleTool` → `StyleRetriever` → `breath_style_guides` collection
- Input: Formatted raw information from retrieval agent
- Output: Cleaned, styled response in Breath app voice
- Constraints: Only uses information from retrieval agent, never adds new facts

**Orchestration** (`run_agent()` in `agent.py`):
- Checks retrieval output for `"NO_RELEVANT_INFORMATION"` → early return
- Passes formatted text to language model if info exists
- Manages tone parameters: `audience_level`, `length`, `energy`, `context`

### Data Flow

1. **Ingestion:**
   - PDFs → `ingest_exercises.py` → ChromaDB `breathing_exercises` collection
   - Style files → `ingest_style.py` → ChromaDB `breath_style_guides` collection

2. **Query Processing:**
   - CLI (`run.py`) parses args → calls `run_agent()`
   - Retrieval agent calls `retrieve_documents` → formats results
   - If no info: return `NO_INFO_MESSAGE` to user
   - If info exists: language model calls `retrieve_style` → styles content → returns final answer

3. **Vector Store:**
   - `ChromaRetriever`: semantic search on `breathing_exercises` (top-k=4)
   - `StyleRetriever`: semantic search on `breath_style_guides` (top-k=4)
   - Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (local, no API cost)

---

## Reasoning & Decision Processes

### Retrieval Agent Reasoning
- **Always calls `retrieve_documents` first** (enforced by system prompt)
- Organizes retrieved chunks into structured sections (overview/steps/benefits/notes)
- **No styling or simplification** — pure extraction and formatting
- Returns sentinel `"NO_RELEVANT_INFORMATION"` when knowledge base has no relevant content

### Control Decision (in `run_agent()`)
- String-based detection: checks for `"NO_RELEVANT_INFORMATION"`, empty responses, or "no information" phrases
- **Short-circuits pipeline** if no info found → prevents hallucination
- Only proceeds to language model if formatted content exists

### Language Model Reasoning
- **Must call `retrieve_style` first** (enforced by prompt)
- Receives formatted raw info + style examples
- Reorganizes and simplifies language while preserving all factual content
- Applies tone parameters (`audience_level`, `length`, `energy`, `context`) to adapt style
- **Cannot add new information** — only rephrases what retrieval agent provided

### Safety & Boundary Decisions
- **Missing content:** Retrieval agent returns sentinel → `run_agent()` returns fixed "I don't know" message
- **Medical advice:** Prompt-level rules enforce hedging language ("may help", "can support") and discourage medical claims
- **Tone adaptation:** System prompt maps tone parameters to style constraints (sentence length, energy level, context framing)

---

## Technical Stack & Design Choices

**Tech Stack:**
- `smolagents` (agent framework)
- Google Gemini 2.5 Flash (LLM)
- ChromaDB (vector database)
- `sentence-transformers` (local embeddings)
- `pypdf/PyPDF2` (PDF extraction)
- LangChain (text chunking)

**Key Design Decisions:**

| Decision | Rationale |
|----------|-----------|
| **Two-LLM architecture** | Clear separation: retrieval/formatting vs. cleaning/styling; prevents information leakage |
| **Style RAG system** | Separate style corpus enables fine-grained voice control without code changes |
| **Dual retrieval** | Content and style retrieved independently; each LLM uses appropriate tools |
| **Local embeddings** | No API costs, works offline, fast retrieval |
| **Source grounding** | Must retrieve before generating; architectural pressure against hallucination |
| **Early return on no-info** | Prevents unnecessary LLM calls and hallucinated responses |
| **Tone parameters** | CLI flags (`--audience-level`, `--length`, `--energy`, `--context`) for fine-tuning |

---

## Evolution: Week 1 → Week 4

| Aspect | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| **Architecture** | Single LLM | Single LLM | Single LLM (optional two-pass) | **Two LLMs (always two-pass)** |
| **Style Control** | None | System prompts | Prompts + style corpus | Prompts + style corpus |
| **Retrieval** | Content only | Content only | Content + Style | Content + Style |
| **Separation** | None | None | None | **Retrieval vs. Language** |

**Key Innovations:**
- **Week 2:** System prompts control output style
- **Week 3:** Style corpus as first-class data source; dual retrieval; tone parameters
- **Week 4:** Two-LLM architecture with clear separation of concerns

---

## Evaluation

### Methodology
- **Qualitative testing:** Variety of queries (4-7-8 breathing, box breathing, anxiety help)
- **Edge cases:** Out-of-scope queries, ambiguous questions
- **Safety checks:** Medical advice handling, hallucination detection
- **Manual inspection:** Compared outputs against source PDFs and style corpus

### PEAS Performance Assessment

**Performance (Accuracy, Style, Edit Effort):**
- **Accuracy:** Steps and benefits match source material when knowledge base contains relevant content
- **Style consistency:** Outputs consistently use short sentences, gentle tone, permission-based language
- **Edit effort:** Typical exercises need only minor phrase tweaks (major improvement over manual writing)

**Environment (CLI, ChromaDB, LLM):**
- CLI is simple and supports both single queries and interactive sessions
- ChromaDB with local embeddings performs well for this corpus size
- Architecture is portable (LLM changes primarily affect `model_utils.py`)

**Actuators (Generation, Retrieval, Style):**
- Clear role separation: retrieval LLM actuates on vector store; language LLM actuates on wording only
- Style retriever successfully injects real style examples into context

**Sensors (Input, Search, Scoring):**
- Simple input handling (CLI args or stdin)
- Semantic search works well for thematic queries and exercise names
- Metadata (titles) preserved in formatted text for attribution context

### Strengths
- **Strong voice consistency:** Style corpus + detailed prompts + always-on style retrieval
- **Low hallucination rate:** Architectural pressure to stay grounded (language model only receives formatted retrieval output)
- **Good controllability:** Four tone parameters provide practical adaptation without re-architecting

### Limitations
- **Coverage limited by corpus:** Only as comprehensive as PDFs in `papers/` directory
- **No explicit citations:** Source titles preserved internally but not exposed in final output
- **Latency:** Two LLM calls per query (retrieval + language) + Chroma queries
- **API dependence:** Requires Gemini API availability and quota
- **Prompt-based safety:** Safety rules not formally verified; could degrade with prompt/model changes

### Improvement Opportunities
- **Evaluation harness:** Fixed query set with metrics (overlap with gold summaries, style similarity)
- **Inline citations:** Preserve source markers in final output or add "show sources" mode
- **Session memory:** Track explained exercises for multi-section content consistency
- **Configurable retrieval:** Expose `max_results` and retrieval modes as CLI/config options

**Overall Assessment:** System meets primary goals — generates calm, on-brand content with minimal editing, stays grounded in sources, has clear control flow suitable for incremental improvements.

---

## Usage

**Setup:**
```bash
# Ingest PDFs into knowledge base
python ingest_exercises.py

# Ingest style examples
python ingest_style.py
```

**Generate Content:**
```bash
# Interactive mode
python run.py

# Single question
python run.py "How do I do 4-7-8 breathing?"

# With tone control
python run.py "Describe box breathing" --audience-level intermediate --energy neutral

# Interactive with parameters
python run.py --chat --context sleep --energy very_gentle
```

---

## Conclusion

Built a two-LLM RAG agent that generates breathing exercise content matching the Breath app voice while staying source-grounded. Key innovations:

- **Two-LLM architecture:** Separates retrieval/formatting from cleaning/styling
- **Style RAG system:** Style corpus as first-class data source with dual retrieval
- **Source grounding:** Architectural constraints prevent hallucination
- **Tone parameters:** Fine-grained style control via CLI flags

The system successfully generates accurate, consistent content with minimal editing, demonstrating clear separation of concerns and a maintainable architecture ready for production use.
