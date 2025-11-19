# Breathing Exercise Content Generator Agent

---

## Problem Description

I'm building a breathing exercise app, and I need to write a lot of content for it exercise descriptions, instructions, benefits, etc. I realized I wanted to be more personal in hand developing the exceirise but did want help on writing out the content. And so as I read and find books and articles that I like I will add them to my url archieve. Along with constant editing of the system prompt to taylor all the content follow the feeling and theme and help me keep a uniform theme with my speak across the whole mobile APP.

### The Problem
- Writing content for each exercise isn't fun
- Im bad at tone and spelling and keeping things uniform
- Keeping it acurate 
- Want content to match my app's calming theme

### My Solution
Built an AI agent that:
- Scrapes articles I choose and stores them in a vector database
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
Basic RAG system that scrapes articles, embeds them, retrieves relevant info, and generates content from sources only.

### Components
- `scraper.py` - Fetches and cleans HTML from URLs
- `ingest_exercises.py` - Chunks text, creates embeddings, stores in ChromaDB
- `tools/vector_store.py` - Semantic search wrapper
- `tools/retrieval_tool.py` - Formats results for agent
- `agent.py` - ReAct agent with source grounding
- `run.py` - Command-line interface

### Testing
- Scraped and embedded articles successfully
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

## PEAS to Code

**Performance → Code**
- Accuracy: `retrieve_documents` tool grounds in sources
- Theme: System instructions in `agent.py` (lines 36-73)
- Boundaries: Says "I don't know" when needed

**Environment → Code**
- Database: ChromaDB in `vector_store/`
- Embeddings: `ingest_exercises.py`
- Interface: `run.py`

**Actuators → Code**
- Generation: Gemini via `model_utils.py`
- Retrieval: `ChromaRetriever` in `tools/vector_store.py`
- Theme: LLM follows system prompts

**Sensors → Code**
- Input: `input()` in `run_interactive_chat()`
- Search: `collection.query()` in ChromaDB
- Scoring: Distance metrics from search

---

## System Architecture

```
Request → run.py → agent.py → retrieval_tool.py → 
vector_store.py → Content → LLM → Themed Output → My App
```

**How It Works**

Setup:
1. Add URLs to `papers/url.txt`
2. Run `ingest_exercises.py`
3. Articles stored in database

Usage:
1. Request content in CLI
2. Agent searches database
3. LLM generates themed content
4. Copy to app

---

## Technical Details

**Tech Stack**
- smolagents (agent framework)
- Google Gemini 2.5 Flash (LLM)
- ChromaDB (vector database)
- sentence-transformers (local embeddings)
- BeautifulSoup (scraping)
- LangChain (chunking)

**Design Choices**

Theme System: Guidelines in prompts, easy to customize, no code changes needed

Local Embeddings: No API costs, works offline

Source Grounding: Must retrieve before generating, won't make things up

Simple Retrieval: Plain text output, easier processing

---

## Week 1 vs Week 2

| Aspect | Week 1 | Week 2 |
|--------|--------|--------|
| Purpose | Basic generation | Production tool |
| Style | Generic | Themed |
| Mode | Single request | Interactive |
| Code | Prototype | Clean |

---

## Usage

Add sources:
```bash
echo "https://health.clevelandclinic.org/4-7-8-breathing" >> papers/url.txt
python ingest_exercises.py
```

Generate content:
```bash
python run.py
```

---

## Conclusion

Built an AI agent that helps me create content for my app. Week 1 got basic RAG working. Week 2 added theme system using customized system prompts.

Main innovation: Comprehensive system prompts control output style. The LLM naturally generates content matching my app's theme without post-processing.

Ready for production use.
