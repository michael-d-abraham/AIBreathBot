#!/usr/bin/env python3
"""Ingests style guide examples from the style/ directory into a ChromaDB collection."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import List

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_STYLE_DIR = SCRIPT_DIR / "style"
DEFAULT_VECTOR_STORE_DIR = SCRIPT_DIR / "vector_store"
DEFAULT_COLLECTION_NAME = "breath_style_guides"


def read_style_files(style_dir: Path) -> List[tuple[str, str]]:
    """Read all .txt files from the style directory.
    
    Args:
        style_dir: Path to the style directory
        
    Returns:
        List of tuples: (filename, content)
    """
    if not style_dir.exists():
        raise ValueError(f"Style directory not found: {style_dir}")
    
    style_files = []
    for txt_file in sorted(style_dir.glob("*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                style_files.append((txt_file.name, content))
    
    return style_files


def parse_args() -> ArgumentParser:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Ingest style guide examples into ChromaDB.")
    parser.add_argument(
        "--style-dir",
        type=Path,
        default=DEFAULT_STYLE_DIR,
        help="Directory containing style .txt files.",
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

    style_dir = args.style_dir
    persist_dir = args.persist_dir
    collection_name = args.collection

    print(f"{'='*60}")
    print(f"Style Guide Ingestion Pipeline")
    print(f"{'='*60}")
    print(f"Style directory: {style_dir}")
    print(f"Vector store: {persist_dir}")
    print(f"Collection: {collection_name}")
    print(f"{'='*60}\n")

    # Step 1: Read style files
    print("Step 1: Reading style files...")
    style_files = read_style_files(style_dir)
    
    if not style_files:
        raise ValueError(f"No .txt files found in {style_dir}")
    
    print(f"Found {len(style_files)} style files.\n")

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
    print("\nStep 3: Processing and ingesting style examples...")
    
    documents: List[str] = []
    metadatas: List[dict] = []
    ids: List[str] = []

    for filename, content in style_files:
        documents.append(content)
        metadatas.append({"source": f"style/{filename}"})
        # Create ID from filename (remove .txt extension)
        doc_id = filename.replace('.txt', '').replace('/', '-')
        ids.append(doc_id)
        print(f"  ✓ Prepared: {filename}")

    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"\n  ✓ Ingested {len(documents)} style examples")

    print(f"\n{'='*60}")
    print(f"Ingestion Complete!")
    print(f"{'='*60}")
    print(f"Style files processed: {len(style_files)}")
    print(f"Total style examples: {len(documents)}")
    print(f"Collection: '{collection_name}'")
    print(f"Vector store: {persist_dir}")
    print(f"\nYou can now use the style retrieval tool in the agent!")


if __name__ == "__main__":
    main()

