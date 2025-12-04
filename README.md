# Breath-AI: Breathing Exercise Content Generator

An AI agent that generates accurate, on-brand breathing exercise content using a two-LLM RAG architecture. Processes PDFs and applies consistent voice styling for the Breath app.

## Overview

This system uses retrieval-augmented generation (RAG) to create breathing exercise content that:
- Stays grounded in source material (no hallucination)
- Matches the Breath app voice consistently
- Adapts tone via fine-tuning parameters
- Requires minimal editing before use

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

1. **User Query** → CLI input
2. **Retrieval Agent** → Searches PDF knowledge base, formats raw information
3. **Language Model** → Retrieves style examples, applies Breath app voice
4. **Output** → Cleaned, styled content ready for use

**Safety:**
- Only uses information from ingested PDFs
- Returns "I don't know" when content isn't available
- Never adds facts not in the knowledge base

## Technical Stack

- **Framework**: smolagents
- **LLM**: Google Gemini 2.5 Flash
- **Vector DB**: ChromaDB (persistent)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local)
- **Text Processing**: LangChain (chunking), PyPDF2 (extraction)

## Adding Content

1. Add PDF files to `papers/` directory
2. Run `python ingest_exercises.py`
3. Vector store is cleared and rebuilt with all PDFs

## Adding Style Examples

1. Add `.txt` files to `style/` directory
2. Run `python ingest_style.py`
3. Style corpus is updated

## License

Educational and personal use.
