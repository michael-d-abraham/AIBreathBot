"""Smolagents Tool wrapper for the Chroma retriever."""

from typing import List

from smolagents import Tool

from .vector_store import ChromaRetriever


class RetrieveDocumentsTool(Tool):
    name = "retrieve_documents"
    description = (
        "Search the breathing exercise knowledge base to find relevant information. "
        "Returns text content from the knowledge base that matches the query."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Question or topic to search for in the knowledge base.",
        },
        "top_k": {
            "type": "integer",
            "description": "Number of text chunks to retrieve.",
            "default": 4,
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, retriever: ChromaRetriever) -> None:
        super().__init__()
        self.retriever = retriever

    def forward(self, query: str, top_k: int = 4) -> str:
        """Return retrieved content as plain text for answering questions."""
        results = self.retriever.retrieve(query=query, limit=top_k)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Combine all retrieved chunks into a simple text format
        content_parts = []
        for i, result in enumerate(results, 1):
            doc_text = result['document']
            source = result['metadata'].get('title', 'Unknown source')
            content_parts.append(f"[Source {i}: {source}]\n{doc_text}")
        
        return "\n\n---\n\n".join(content_parts)
