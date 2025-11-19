# Breathing Exercise Chatbot

An AI chatbot that answers questions about breathing exercises using retrieval-augmented generation (RAG) from a curated knowledge base.

## Overview

The Breathing Exercise Chatbot is built with the smolagents framework and provides an interactive way to learn about breathing exercises. The system scrapes breathing exercise content from URLs, stores it in a vector database (ChromaDB), and uses semantic search to answer your questions based strictly on the knowledge base.

## Key Features

✅ **Interactive Chat Mode**: Have a conversation with the chatbot and ask multiple questions  
✅ **Single Question Mode**: Ask one question and get an answer quickly  
✅ **Easy URL Management**: Add/remove URLs in `papers/url.txt` and rerun ingestion  
✅ **Web Scraping**: Automatically fetches and cleans content from breathing exercise websites  
✅ **Vector Database**: Stores content in ChromaDB for fast semantic search  
✅ **Strict Knowledge Boundaries**: Chatbot only answers from your knowledge base, no external searches  
✅ **No Hallucinations**: Says "I don't know" when information isn't in the knowledge base

## Project Structure

```
Breath-AI/
├── agent.py                  # Chatbot agent with RAG capabilities
├── run.py                    # Entry point (interactive & single-question modes)
├── model_utils.py            # Model initialization (Gemini API)
├── scraper.py                # URL scraping logic
├── ingest_exercises.py       # Ingestion pipeline (URLs → ChromaDB)
├── requirements.txt          # Python dependencies
├── .env                      # API keys (create this file)
├── tools/
│   ├── retrieval_tool.py     # Retrieval tool for searching exercises
│   └── vector_store.py       # ChromaDB wrapper
├── papers/
│   └── url.txt               # URLs to scrape (one per line)
└── vector_store/             # ChromaDB database (created after ingestion)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

Get a Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Add URLs

Edit `papers/url.txt` and add URLs to breathing exercise pages (one per line):

```
"https://health.clevelandclinic.org/4-7-8-breathing"
"https://example.com/another-breathing-exercise"
```

### 4. Ingest the Content

Run the ingestion pipeline to scrape URLs and populate the vector database:

```bash
python ingest_exercises.py
```

This will:
- Read URLs from `papers/url.txt`
- Scrape each URL using BeautifulSoup
- Extract and clean the text content
- Chunk the content into smaller pieces
- Store everything in ChromaDB with embeddings

You should see output like:
```
============================================================
Breathing Exercise Ingestion Pipeline
============================================================
Scraping: https://health.clevelandclinic.org/4-7-8-breathing
  ✓ Success: 8234 characters extracted

Successfully scraped 1 out of 1 URLs.

✓ Ingested 16 chunks from: How To Do the 4-7-8 Breathing Exercise
============================================================
```

## Usage

### Interactive Chat Mode (Default)

Start an interactive conversation with the chatbot:

```bash
# Run without arguments for interactive mode
python run.py

# Or explicitly use the --chat flag
python run.py --chat
```

**Example conversation:**

```bash
$ python run.py

============================================================
Breathing Exercise Chatbot - Interactive Mode
============================================================

Ask questions about breathing exercises from the knowledge base.
Type 'exit', 'quit', or press Ctrl+C to end the conversation.

🫁 You: How do I do 4-7-8 breathing?

🤖 Chatbot: [Retrieves and answers based on knowledge base]

🫁 You: What are the benefits of this technique?

🤖 Chatbot: [Answers based on knowledge base]

🫁 You: exit

👋 Goodbye! Take care of your breathing!
```

### Single Question Mode

Ask a single question and get an immediate answer:

```bash
python run.py "How do I do 4-7-8 breathing?"
python run.py "What are the benefits of breathing exercises?"
python run.py "What breathing technique helps with anxiety?"
```

**Example:**

```bash
$ python run.py "How do I do 4-7-8 breathing?"

============================================================
Breathing Exercise Chatbot
============================================================

Query: How do I do 4-7-8 breathing?

[Chatbot retrieves documents and provides answer]
```

### How It Works

The chatbot will:
1. Use semantic search to retrieve relevant content from your knowledge base
2. Answer your question using ONLY information from the retrieved documents
3. Say "I don't know" if the information isn't in the knowledge base
4. Never use external knowledge or search the internet

## Knowledge Base Management

### Adding New URLs

1. Edit `papers/url.txt`
2. Add new URLs (one per line, optionally in quotes)
3. Rerun ingestion: `python ingest_exercises.py`

The vector database will be cleared and rebuilt with all URLs.

### Removing URLs

1. Remove URLs from `papers/url.txt`
2. Rerun ingestion: `python ingest_exercises.py`

## Technical Details

- **Agent Framework**: smolagents (ReAct agent)
- **LLM**: Google Gemini 2.5 Flash
- **Vector Database**: ChromaDB with persistent storage
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Text Chunking**: RecursiveCharacterTextSplitter (500 chars, 100 overlap)
- **Web Scraping**: BeautifulSoup + requests

## Strict Knowledge Boundaries

The chatbot is designed with **strict knowledge boundaries**:

- ✅ Only answers from retrieved documents in your knowledge base
- ✅ Always retrieves relevant content before answering
- ✅ Explicitly says "I don't know" when information is not available
- ✅ Never searches the internet or external sources
- ❌ Does not use general knowledge about breathing exercises
- ❌ Does not make up information

This ensures reliable, verifiable answers based solely on your curated knowledge base.

## Troubleshooting

### "No content found in knowledge base"
Run the ingestion pipeline first: `python ingest_exercises.py`

### "All URL scraping attempts failed"
- Check your internet connection
- Verify URLs in `papers/url.txt` are valid
- Check if the websites are accessible

### Chatbot says "I don't know" too often
- Add more URLs to `papers/url.txt` to expand your knowledge base
- Make sure the content you're asking about is actually in the scraped pages
- Try rephrasing your question

### Linter Warnings
The project uses type hints and follows Python best practices. Run:
```bash
python -m py_compile agent.py scraper.py ingest_exercises.py
```

## Example Workflow

```bash
# 1. Setup
pip install -r requirements.txt
echo 'GEMINI_API_KEY=your_key' > .env

# 2. Add URLs to your knowledge base
echo '"https://health.clevelandclinic.org/4-7-8-breathing"' > papers/url.txt

# 3. Scrape and embed the content
python ingest_exercises.py

# 4. Start chatting! (Interactive mode)
python run.py

# Or ask a single question
python run.py "How do I do 4-7-8 breathing?"
```

## License

This project is for educational and personal use.
