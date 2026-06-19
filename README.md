# Breath-AI: Breathing Exercise Content Generator

An AI agent that generates accurate, on-brand breathing exercise content using a two-LLM RAG architecture. Processes PDFs and applies consistent voice styling for the Breath app.

## 🎯 Why This Exists

Creating consistent, accurate breathing exercise descriptions for a mobile wellness app is challenging:
- **Consistency**: Maintaining uniform tone and style across dozens of exercises
- **Accuracy**: Ensuring all content is grounded in scientific research
- **Time**: Reducing manual writing and editing from hours to minutes
- **Brand Voice**: Matching the app's specific voice (warm, gentle, permission-based)

This system automates the process while ensuring accuracy and brand consistency.

## Overview

This system uses retrieval-augmented generation (RAG) to create breathing exercise content that:
- ✅ Stays grounded in source material (no hallucination)
- ✅ Matches the Breath app voice consistently
- ✅ Adapts tone via fine-tuning parameters
- ✅ Requires minimal editing before use
- ✅ Returns "I don't know" when information isn't available (never invents facts)

## 🌟 Key Features

### Two-LLM Architecture
- **Retrieval Agent (LLM 1)**: Focuses solely on finding and formatting raw information
- **Language Model (LLM 2)**: Focuses solely on cleaning, simplifying, and applying brand voice
- Clear separation of concerns prevents information leakage and improves maintainability

### Style RAG System
- Separate style corpus stored in vector database
- Language model retrieves style examples to guide output
- Update app voice by adding style examples, not rewriting code

### Source-Grounded Design
- Architecturally constrained to only use information from ingested PDFs
- Early return mechanism: stops pipeline if no relevant information found
- Prevents hallucination through design, not just prompts

### Fine-Grained Tone Control
- Four parameters adapt output for different contexts and audiences
- Same exercise can be described differently for sleep vs. pre-workout
- Maintains brand voice while adapting to context

## Architecture

**Two-LLM Pipeline:**
1. **Retrieval Agent**: Extracts and formats information from PDF knowledge base
2. **Language Model**: Cleans, simplifies, and applies Breath app voice styling

**Key Components:**
- ChromaDB vector store (content + style corpus)
- Local embeddings (sentence-transformers/all-MiniLM-L6-v2)
- Google Gemini 2.5 Flash (LLM)
- Style corpus for voice consistency

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

Get your key from: https://aistudio.google.com/app/apikey

### 3. Ingest Content

**Ingest PDFs:**
```bash
python ingest_exercises.py
```

Place PDF files in the `papers/` directory. The script will:
- Extract text from all PDFs
- Chunk content (500 chars, 100 overlap)
- Store in ChromaDB with embeddings

**Ingest Style Examples:**
```bash
python ingest_style.py
```

Processes `.txt` files from `style/` directory to build the voice corpus.

## Usage

### Interactive Mode

```bash
python run.py --chat
```

### Single Query

```bash
python run.py "How do I do 4-7-8 breathing?"
```

### Tone Control

Fine-tune output style with parameters:

```bash
python run.py "Describe box breathing" \
  --audience-level intermediate \
  --length long \
  --energy neutral \
  --context pre-work
```

**Available Parameters:**
- `--audience-level`: `beginner` | `intermediate`
- `--length`: `short` | `medium` | `long`
- `--energy`: `very_gentle` | `neutral` | `slightly_uplifting`
- `--context`: `sleep` | `mid-day_reset` | `pre-work` | `anxiety_spike` | `general`

## Project Structure

```
Breath-AI/
├── agent.py              # Two-LLM agent architecture
├── run.py                # CLI entry point
├── model_utils.py        # Gemini model configuration
├── ingest_exercises.py   # PDF → ChromaDB pipeline
├── ingest_style.py       # Style corpus ingestion
├── scraper.py            # PDF text extraction
├── papers/               # PDF knowledge base
├── style/                # Style guide examples
└── vector_store/         # ChromaDB persistence
```

## How It Works

### Data Flow

```
User Query (CLI)
    ↓
┌─────────────────────────────┐
│ Retrieval Agent (LLM 1)     │
│ • Searches PDF knowledge     │
│   base via ChromaDB          │
│ • Formats raw information   │
│ • Returns formatted text    │
└─────────────────────────────┘
    ↓ (if info found)
┌─────────────────────────────┐
│ Language Model (LLM 2)      │
│ • Retrieves style examples  │
│ • Cleans & simplifies       │
│ • Applies Breath app voice  │
│ • Uses tone parameters      │
└─────────────────────────────┘
    ↓
Styled, Production-Ready Content
```

### Detailed Process

1. **User Query** → CLI input with optional tone parameters
2. **Retrieval Agent** → 
   - Searches PDF knowledge base using semantic search
   - Formats raw information into structured sections
   - Returns "NO_RELEVANT_INFORMATION" if nothing found
3. **Early Return Check** → 
   - If no information found, returns "I don't have that information"
   - Prevents unnecessary LLM calls and hallucination
4. **Language Model** → 
   - Retrieves style examples from style corpus
   - Cleans and simplifies the formatted information
   - Applies Breath app voice using style examples
   - Adapts tone based on parameters (audience, length, energy, context)
5. **Output** → Cleaned, styled content ready for use

### Safety Mechanisms

- **Source Grounding**: Only uses information from ingested PDFs
- **Early Return**: Stops pipeline if no relevant information found
- **No Direct Access**: Language model can't access original knowledge base directly
- **Explicit Boundaries**: Returns "I don't know" rather than guessing
- **Medical Safety**: Uses hedging language ("may help", "can support") instead of claims

## Technical Stack

- **Framework**: smolagents (lightweight agent framework)
- **LLM**: Google Gemini 2.5 Flash (via OpenAI-compatible API)
- **Vector DB**: ChromaDB (persistent, two collections: content + style)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local, no API costs)
- **Text Processing**: LangChain (chunking), PyPDF2 (extraction)

### Why These Choices?

- **Local Embeddings**: Zero API costs for semantic search, works offline, fast
- **ChromaDB**: Simple, persistent, perfect for this corpus size
- **Two Collections**: Separate content and style retrieval enables independent optimization
- **smolagents**: Lightweight framework that doesn't hide complexity

## Adding Content

1. Add PDF files to `papers/` directory
2. Run `python ingest_exercises.py`
3. Vector store is cleared and rebuilt with all PDFs

## Adding Style Examples

1. Add `.txt` files to `style/` directory
2. Run `python ingest_style.py`
3. Style corpus is updated

## Example Usage

### Basic Query
```bash
python run.py "How do I do 4-7-8 breathing?"
```

### Context-Specific Content
```bash
# For bedtime
python run.py "Describe deep breathing" --context sleep --energy very_gentle

# For pre-workout
python run.py "Describe box breathing" --context pre-work --energy slightly_uplifting
```

### Interactive Mode
```bash
python run.py --chat --audience-level intermediate
```

## Limitations & Future Improvements

### Current Limitations
- Coverage limited by PDFs in knowledge base
- Two LLM calls per query (latency consideration)
- No explicit citations in final output
- Requires Gemini API availability

### Potential Improvements
- Evaluation harness with metrics
- Inline citations or "show sources" mode
- Session memory for multi-section consistency
- Configurable retrieval parameters

## License

Educational and personal use.
