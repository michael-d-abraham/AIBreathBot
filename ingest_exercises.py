#!/usr/bin/env python3
"""Ingests breathing exercise content from URLs into a ChromaDB collection."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

from scraper import scrape_all_urls


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_URL_FILE = SCRIPT_DIR / "papers" / "url.txt"
DEFAULT_VECTOR_STORE_DIR = SCRIPT_DIR / "vector_store"
DEFAULT_COLLECTION_NAME = "breathing_exercises"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str) -> Iterable[str]:
    """Split text into chunks using recursive character text splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    return splitter.split_text(text)


def ingest_scraped_content(scraped_data: dict) -> tuple[list[str], list[dict], list[str]]:
    """Process scraped content by chunking it and creating metadata.
    
    Args:
        scraped_data: Dictionary with 'url', 'title', 'content', 'status', 'error'
        
    Returns:
        Tuple of (documents, metadatas, ids)
    """
    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    # Skip if scraping failed or no content
    if scraped_data['status'] != 'success' or not scraped_data['content'].strip():
        return documents, metadatas, ids
    
    url = scraped_data['url']
    title = scraped_data['title']
    content = scraped_data['content']
    
    # Create a safe ID from the URL
    url_id = url.replace('https://', '').replace('http://', '').replace('/', '-').replace('.', '-')
    # Limit length
    url_id = url_id[:50]
    
    chunks = list(chunk_text(content))
    
    for chunk_index, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({
            "url": url,
            "title": title,
            "chunk_index": chunk_index,
        })
        ids.append(f"{url_id}-c{chunk_index}")

    return documents, metadatas, ids


def parse_args() -> ArgumentParser:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Ingest breathing exercise content into ChromaDB.")
    parser.add_argument(
        "--url-file",
        type=Path,
        default=DEFAULT_URL_FILE,
        help="File containing URLs to scrape (one per line).",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=DEFAULT_VECTOR_STORE_DIR,
        help="Directory for the ChromaDB persistence layer.",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION_NAME,
        help="Target ChromaDB collection name.",
    )
    return parser


def main() -> None:
    """Main ingestion function."""
    parser = parse_args()
    args = parser.parse_args()

    url_file = args.url_file
    persist_dir = args.persist_dir
    collection_name = args.collection

    print(f"{'='*60}")
    print(f"Breathing Exercise Ingestion Pipeline")
    print(f"{'='*60}")
    print(f"URL file: {url_file}")
    print(f"Vector store: {persist_dir}")
    print(f"Collection: {collection_name}")
    print(f"{'='*60}\n")

    # Step 1: Scrape all URLs
    print("Step 1: Scraping URLs...")
    scraped_results = scrape_all_urls(url_file, timeout=15)
    
    if not scraped_results:
        raise ValueError(f"No URLs scraped from {url_file}")
    
    successful_scrapes = [r for r in scraped_results if r['status'] == 'success']
    
    if not successful_scrapes:
        raise ValueError("All URL scraping attempts failed. Check the URLs and your internet connection.")
    
    print(f"\nSuccessfully scraped {len(successful_scrapes)} out of {len(scraped_results)} URLs.\n")

    # Step 2: Initialize ChromaDB
    print("Step 2: Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=str(persist_dir))
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=collection_name, embedding_function=embedding_fn
    )

    # Clear existing data
    if collection.count() > 0:
        print(f"Clearing existing {collection.count()} documents from collection.")
        collection.delete(ids=collection.get()["ids"])

    # Step 3: Process and ingest content
    print("\nStep 3: Processing and ingesting content...")
    total_chunks = 0

    for scraped_data in successful_scrapes:
        documents, metadatas, ids = ingest_scraped_content(scraped_data)

        if not documents:
            print(f"Skipping {scraped_data['url']}: no content to ingest.")
            continue

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        total_chunks += len(documents)
        print(f"  ✓ Ingested {len(documents)} chunks from: {scraped_data['title'][:60]}")

    print(f"\n{'='*60}")
    print(f"Ingestion Complete!")
    print(f"{'='*60}")
    print(f"URLs processed: {len(successful_scrapes)}")
    print(f"Total chunks: {total_chunks}")
    print(f"Collection: '{collection_name}'")
    print(f"Vector store: {persist_dir}")
    print(f"\nYou can now run the agent to query the breathing exercises!")


if __name__ == "__main__":
    main()

