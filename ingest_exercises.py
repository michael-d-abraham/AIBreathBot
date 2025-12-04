#!/usr/bin/env python3


"""Ingests breathing exercise content from local PDF files into a ChromaDB collection."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

from scraper import extract_pdf_content_from_file


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PAPERS_DIR = SCRIPT_DIR / "papers"
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


def process_pdf_file(pdf_path: Path) -> tuple[list[str], list[dict], list[str]]:
    """Process a PDF file by extracting content, chunking it, and creating metadata.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (documents, metadatas, ids)
    """
    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    try:
        title, content = extract_pdf_content_from_file(pdf_path)
    except Exception as e:
        # Return empty lists if extraction fails
        return documents, metadatas, ids
    
    # Skip if no content extracted
    if not content.strip():
        return documents, metadatas, ids
    
    # Create a safe ID from the filename
    file_id = pdf_path.stem.replace(' ', '-').replace('_', '-').replace('.', '-')
    # Limit length
    file_id = file_id[:50]
    
    chunks = list(chunk_text(content))
    
    for chunk_index, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({
            "source": str(pdf_path.name),
            "title": title,
            "chunk_index": chunk_index,
        })
        ids.append(f"{file_id}-c{chunk_index}")

    return documents, metadatas, ids


def parse_args() -> ArgumentParser:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Ingest breathing exercise content from PDF files into ChromaDB.")
    parser.add_argument(
        "--papers-dir",
        type=Path,
        default=DEFAULT_PAPERS_DIR,
        help="Directory containing PDF files to ingest.",
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

    papers_dir = args.papers_dir
    persist_dir = args.persist_dir
    collection_name = args.collection

    print(f"{'='*60}")
    print(f"Breathing Exercise Ingestion Pipeline")
    print(f"{'='*60}")
    print(f"PDF directory: {papers_dir}")
    print(f"Vector store: {persist_dir}")
    print(f"Collection: {collection_name}")
    print(f"{'='*60}\n")

    # Step 1: Find all PDF files
    print("Step 1: Finding PDF files...")
    if not papers_dir.exists():
        raise ValueError(f"PDF directory not found: {papers_dir}")
    
    pdf_files = list(papers_dir.glob("*.pdf"))
    
    if not pdf_files:
        raise ValueError(f"No PDF files found in {papers_dir}")
    
    print(f"Found {len(pdf_files)} PDF file(s).\n")

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
    successful_files = 0

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        documents, metadatas, ids = process_pdf_file(pdf_path)

        if not documents:
            print(f"  ✗ Skipping {pdf_path.name}: no content extracted.")
            continue

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        total_chunks += len(documents)
        successful_files += 1
        print(f"  ✓ Ingested {len(documents)} chunks from: {pdf_path.name}")

    print(f"\n{'='*60}")
    print(f"Ingestion Complete!")
    print(f"{'='*60}")
    print(f"PDF files processed: {successful_files} out of {len(pdf_files)}")
    print(f"Total chunks: {total_chunks}")
    print(f"Collection: '{collection_name}'")
    print(f"Vector store: {persist_dir}")
    print(f"\nYou can now run the agent to query the breathing exercises!")


if __name__ == "__main__":
    main()

