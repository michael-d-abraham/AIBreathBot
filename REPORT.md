# Breathing Exercise Content Generator Agent

git repo: https://github.com/michael-d-abraham/AIBreathBot
---

## Problem Description

I'm building a breathing exercise app, and I need to write a lot of content for it exercise descriptions, instructions, benefits, etc. I realized I wanted to be more personal in hand developing the exceirise but did want help on writing out the content. And so as I read and find books and articles that I like I will download PDFs and add them to my papers directory. Along with constant editing of the system prompt to taylor all the content follow the feeling and theme and help me keep a uniform theme with my speak across the whole mobile APP.

### The Problem
- Writing content for each exercise isn't fun
- Im bad at tone and spelling and keeping things uniform
- Keeping it acurate 
- Want content to match my app's calming theme


### My Solution
Built an AI agent that:
- Processes local PDF files I download and stores them in a vector database
- Retrieves relevant info when I need it
- Generates content using customized theme prompts
- Only uses information from sources (no hallucinations)

I ask for content and it generates text in my app's style. Then I copy it to my project.

---

## PEAS Framework

**Performance:** Content is accurate, matches my theme, beginner-friendly, needs minimal editing

**Environment:** CLI interface, ChromaDB database, theme system, Gemini LLM

**Actuators:** Generates themed content, searches database, applies style guidelines, manages sessions

**Sensors:** Receives requests, searches with semantic similarity, gets relevant chunks, tracks context

---

## Week 1: Basic Prototype

### What I Built
Basic RAG system that processes local PDF files, extracts text, embeds them, retrieves relevant info, and generates content from sources only.

### Components
- `scraper.py` - Extracts text content from local PDF files
- `ingest_exercises.py` - Processes PDFs, chunks text, creates embeddings, stores in ChromaDB
- `tools/vector_store.py` - Semantic search wrapper
- `tools/retrieval_tool.py` - Formats results for agent
- `agent.py` - ReAct agent with source grounding
- `run.py` - Command-line interface

### Testing
- Processed and embedded PDF files successfully
- Retrieved relevant content accurately
- Generated content only from sources
- Refused requests outside knowledge base

### Challenges
- Too much metadata in retrieval
- Generic output tone
- No multi-request sessions
- Couldn't control style

---

## Week 2: Theme System

### What I Added
- Interactive mode for multiple requests
- Theme system to control output style
- Simplified retrieval
- Language guidelines
- Code cleanup

### Theme System (Key Feature)

The main innovation is language guidelines in system prompts that control output style.

Current theme: Calming and mindful for beginners

Guidelines:
- Warm, calming language with present-moment words
- Say "you might" not "you must"
- Say "this can support" not "this will fix"
- Simple steps, no jargon

Example:
```
"The 4-7-8 breathing technique invites you to gently slow your breath, 
creating a natural rhythm. You might notice a sense of calm as you 
breathe in for 4 counts, hold softly for 7, and exhale slowly for 8."
```

Easy to modify themes by editing system prompts without code changes.

### Other Changes
- Interactive mode: multiple requests in one session
- Simplified retrieval: plain text instead of complex objects
- Removed unused JSON extraction code

### Testing
- Interactive mode works well
- Content matches theme consistently
- Voice stays uniform
- No hallucination
- Content ready with minimal editing

---

## Week 3: Style RAG System

### What I Added
- Separate style corpus with golden examples
- Style ingestion pipeline (`ingest_style.py`)
- Dual retrieval system (content + style)
- Tightened and centralized system prompt
- Two-pass generation mode (optional)
- Tone control parameters

### Style RAG System (Key Feature)

The main innovation is treating "style" as a first-class data source, separate from factual breathing content.

**Style Corpus:**
- Separate `style/` directory with golden example texts
- Examples demonstrate desired tone: warm, gentle, permission-based language
- Files like `golden_intro_1.txt`, `gentle_closings.txt`, `short_exercise_examples.txt`
- Stored in separate ChromaDB collection: `breath_style_guides`

**Dual Retrieval:**
- Agent retrieves both factual content AND style examples
- Content retrieval: factual information about breathing exercises
- Style retrieval: tone/phrasing examples from style corpus
- Agent uses CONTENT for facts, STYLE_EXAMPLES for voice

**How It Works:**
1. User asks about a breathing exercise
2. Agent calls `retrieve_documents` → gets factual content
3. Agent calls `retrieve_style` → gets style examples matching query
4. Agent generates response using both:
   - Facts from CONTENT
   - Tone/phrasing inspired by STYLE_EXAMPLES
5. Output matches Breath app voice while staying source-grounded

**System Prompt:**
Centralized comprehensive prompt defining:
- Breath app voice identity
- Tone guidelines (warm, grounded, calm, permission-based)
- Language preferences (short sentences, concrete sensations, avoid clinical terms)
- Safety rules (no medical claims, hedging language)
- Default output structure (overview → steps → closing)

**Two-Pass Mode:**
Optional mode for extra control:
- Pass 1: Generate neutral, factual description (content only)
- Pass 2: Rewrite in Breath voice using style examples
- Exposed via `--two-pass` CLI flag

**Tone Control Parameters:**
Fine-tune output style:
- `--audience-level`: beginner | intermediate
- `--length`: short | medium | long
- `--energy`: very_gentle | neutral | slightly_uplifting
- `--context`: sleep | mid-day_reset | pre-work | anxiety_spike | general

### New Components
- `style/` directory - Golden example texts
- `ingest_style.py` - Ingests style examples into ChromaDB
- `StyleRetriever` class in `tools/vector_store.py` - Retrieves style examples
- `RetrieveStyleTool` in `tools/retrieval_tool.py` - Agent tool for style retrieval
- Updated `agent.py` - Dual retrieval, comprehensive system prompt
- Updated `run.py` - CLI flags for two-pass mode and tone parameters

### Testing
- Style files ingest successfully into separate collection
- Style retrieval returns relevant examples
- Agent calls both content and style tools automatically
- Generated content matches Breath voice consistently
- Still refuses queries outside knowledge base
- Two-pass mode produces neutral then styled output
- Tone parameters affect output appropriately
- Interactive mode works with all new features

---

## Week 4: Two-LLM Architecture

### What I Changed
- Separated retrieval/formatting from language cleaning/styling into two distinct LLMs
- Always-on two-pass architecture (no longer optional)
- Improved error handling for missing information
- Clear separation of concerns between agents

### Two-LLM Architecture (Key Feature)

The main innovation is separating the agent into two specialized LLMs with distinct responsibilities.

**Retrieval Agent (First LLM):**
- Retrieves raw information from knowledge base using `retrieve_documents`
- Formats retrieved information in clear, organized plain text
- Includes all relevant facts, steps, and details
- Organizes information logically (overview, steps, benefits, notes)
- Returns early if no relevant information found
- **No styling, no simplification** - just retrieval and formatting

**Language Model (Second LLM):**
- Receives formatted raw information from retrieval agent
- Cleans and simplifies language
- Applies Breath app voice style using retrieved style examples
- Uses tunable variables (audience_level, length, energy, context)
- **Only uses information from first LLM** - never adds new information
- Can simplify and rephrase, but keeps all factual content

**Flow:**
```
User Query
    ↓
Retrieval Agent (First LLM)
    ├─ Retrieves raw info from knowledge base
    ├─ Formats it in plain text
    └─ If no info found → Return early to user
    ↓
Language Model (Second LLM)
    ├─ Receives formatted raw information
    ├─ Retrieves style examples
    ├─ Cleans and simplifies language
    ├─ Applies Breath app voice style
    ├─ Uses tunable variables (audience_level, length, energy, context)
    └─ Returns ONLY information from first LLM (no additions)
    ↓
User receives cleaned and styled response
```

**Key Benefits:**
- Clear separation: retrieval/formatting vs. cleaning/styling
- Better control: each LLM has focused responsibility
- No information leakage: second LLM cannot add information not in first LLM's output
- Improved error handling: early return when no information found
- Always two-pass: consistent architecture for all queries

### Changes Made
- Refactored `agent.py` with `_build_retrieval_agent()` and `_build_language_model()` functions
- New `run_agent()` function orchestrates the two-pass flow
- Updated `run.py` to always use two-pass architecture (removed `--two-pass` flag)
- Improved error detection for "no information" cases
- Maintained backward compatibility with legacy functions

### Testing
- Two-LLM flow works correctly
- Retrieval agent formats information properly
- Language model cleans and styles without adding information
- Early return works when no information found
- Tunable variables still work correctly
- Style examples still retrieved and applied

---

## PEAS to Code

**Performance → Code**
- Accuracy: `retrieve_documents` tool grounds in sources
- Theme: System instructions in `agent.py` + style corpus retrieval
- Boundaries: Says "I don't know" when needed
- Voice consistency: `retrieve_style` tool provides tone examples

**Environment → Code**
- Database: ChromaDB in `vector_store/` (two collections: content + style)
- Embeddings: `ingest_exercises.py` (content) + `ingest_style.py` (style)
- Interface: `run.py` with tone control parameters

**Actuators → Code**
- Generation: Gemini via `model_utils.py` (used by both LLMs)
- Content Retrieval: `ChromaRetriever` in `tools/vector_store.py`
- Style Retrieval: `StyleRetriever` in `tools/vector_store.py`
- Retrieval Agent: `_build_retrieval_agent()` in `agent.py`
- Language Model: `_build_language_model()` in `agent.py`
- Orchestration: `run_agent()` function in `agent.py`

**Sensors → Code**
- Input: `input()` in `run_interactive_chat()`
- Content Search: `collection.query()` in ChromaDB (breathing_exercises)
- Style Search: `collection.query()` in ChromaDB (breath_style_guides)
- Scoring: Distance metrics from semantic search

---

## System Architecture

### Two-LLM Architecture Flow

```
User Query
    ↓
┌─────────────────────────────────────┐
│  Retrieval Agent (First LLM)        │
│  - Uses retrieve_documents tool     │
│  - Retrieves raw info from KB       │
│  - Formats in plain text            │
│  - Organizes logically               │
└─────────────────────────────────────┘
    ↓
    ├─ If no info found → Return early
    ↓
    └─ Formatted Raw Information
    ↓
┌─────────────────────────────────────┐
│  Language Model (Second LLM)        │
│  - Uses retrieve_style tool         │
│  - Receives formatted raw info      │
│  - Cleans and simplifies language   │
│  - Applies Breath app voice style   │
│  - Uses tunable variables           │
│  - NO information addition          │
└─────────────────────────────────────┘
    ↓
Cleaned and Styled Response → User
```

### Component Details

**Retrieval Agent:**
- Tool: `RetrieveDocumentsTool` → `ChromaRetriever` → `breathing_exercises` collection
- Output: Formatted plain text with all relevant facts
- Error handling: Returns early if no information found

**Language Model:**
- Tool: `RetrieveStyleTool` → `StyleRetriever` → `breath_style_guides` collection
- Input: Formatted raw information from retrieval agent
- Output: Cleaned and styled response in Breath app voice
- Constraints: Only uses information from retrieval agent, never adds new info

**How It Works**

Setup:
1. Download PDF files and place them in `papers/` directory
2. Run `ingest_exercises.py` → processes PDFs and stores factual content in `breathing_exercises` collection
3. Add style examples to `style/` directory
4. Run `ingest_style.py` → stores style examples in `breath_style_guides` collection
5. Both collections ready in ChromaDB

Usage:
1. Request content in CLI (with tone parameters: audience_level, length, energy, context)
2. Retrieval Agent retrieves and formats raw information
3. Language Model retrieves style examples, cleans and styles the information
4. Receive cleaned and styled response ready for app

---

## Technical Details

**Tech Stack**
- smolagents (agent framework)
- Google Gemini 2.5 Flash (LLM)
- ChromaDB (vector database)
- sentence-transformers (local embeddings)
- pypdf/PyPDF2 (PDF text extraction)
- LangChain (chunking)

**Design Choices**

Two-LLM Architecture: Always-on separation of retrieval/formatting from cleaning/styling ensures clear responsibilities and prevents information leakage

Style RAG: Separate style corpus from content, enables fine-grained voice control

Dual Retrieval: Content and style retrieved separately, each LLM uses appropriate tools

System Prompt Centralization: Voice rules in comprehensive prompts for each LLM

Two Collections: Clear separation between factual content and style examples

No Chunking for Style: Style examples are short, stored as-is

Tone Parameters: CLI flags for fine-tuning output style (audience_level, length, energy, context)

Local Embeddings: No API costs, works offline

Source Grounding: Must retrieve before generating, won't make things up

Simple Retrieval: Plain text output, easier processing

Error Handling: Early return when no information found, prevents unnecessary processing

---

## Week 1 vs Week 2 vs Week 3 vs Week 4

| Aspect | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| Purpose | Basic generation | Production tool | Production tool + voice control | Production tool + separated concerns |
| Style | Generic | Themed (prompts) | Themed (prompts + style corpus) | Themed (prompts + style corpus) |
| Retrieval | Content only | Content only | Content + Style (dual) | Content + Style (dual) |
| Architecture | Single LLM | Single LLM | Single LLM (optional two-pass) | Two LLMs (always two-pass) |
| Mode | Single request | Interactive | Interactive + optional two-pass | Interactive (always two-pass) |
| Voice Control | None | System prompt | System prompt + style examples + tone params | System prompt + style examples + tone params |
| Separation | None | None | None | Retrieval/formatting vs. cleaning/styling |
| Code | Prototype | Clean | Extended | Refactored with clear separation |

---

## Usage

Add content sources:
```bash
# Download PDF files and place them in papers/ directory
# Then run:
python ingest_exercises.py
```

Add style examples:
```bash
# Edit files in style/ directory, then:
python ingest_style.py
```

Generate content:
```bash
# Interactive mode (default)
python run.py

# Single question
python run.py "How do I do 4-7-8 breathing?"

# With tone control
python run.py "Describe box breathing" --audience-level intermediate --energy neutral

# Interactive with parameters
python run.py --chat --context sleep --energy very_gentle

# Note: Two-pass architecture is always active (no --two-pass flag needed)
```

---

## Conclusion

Built an AI agent that helps me create content for my app. Week 1 got basic RAG working. Week 2 added theme system using customized system prompts. Week 3 added style RAG system with dual retrieval. Week 4 refactored to a two-LLM architecture with clear separation of concerns.

Main innovations:
- Week 2: Comprehensive system prompts control output style
- Week 3: Style corpus as first-class data source, dual retrieval (content + style), tone control parameters
- Week 4: Two-LLM architecture separating retrieval/formatting from cleaning/styling

The system now uses a two-LLM architecture:
1. **Retrieval Agent** retrieves and formats raw information from the knowledge base
2. **Language Model** cleans, simplifies, and styles the information using golden style files and tunable variables

This separation ensures:
- Clear responsibilities for each LLM
- No information leakage (second LLM only uses information from first LLM)
- Better error handling (early return when no information found)
- Consistent architecture for all queries (always two-pass)

The agent retrieves both factual content and style examples, generating responses that match the Breath app voice while staying source-grounded. Tone parameters allow fine-tuning for different contexts (audience_level, length, energy, context).

Ready for production use with enhanced voice consistency and clear architectural separation.
