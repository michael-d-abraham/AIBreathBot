"""Breathing Exercise Agent: A chatbot for answering questions about breathing exercises.

This module implements a two-LLM architecture:
1. Retrieval Agent: Retrieves raw information from knowledge base and formats it
2. Language Model: Cleans, simplifies, and styles the information using golden style files
"""

from pathlib import Path
from smolagents import ToolCallingAgent
import model_utils
from tools.retrieval_tool import RetrieveDocumentsTool, RetrieveStyleTool
from tools.vector_store import ChromaRetriever, StyleRetriever


# Constants for early return messages
NO_INFO_MESSAGE = "I don't have that information in my knowledge base at the moment."


def _build_retrieval_agent(
    content_retriever: ChromaRetriever,
    verbose: int = 1,
) -> ToolCallingAgent:
    """Build the retrieval agent (first LLM) that retrieves and formats raw information.
    
    Args:
        content_retriever: ChromaDB retriever for breathing exercise content
        verbose: Verbosity level for agent output
        
    Returns:
        ToolCallingAgent configured for retrieval and formatting
    """
    model = model_utils.google_build_reasoning_model()
    
    retrieval_prompt = """You are a retrieval and formatting agent for breathing exercise information.

Your job:
1. Retrieve relevant information from the knowledge base using retrieve_documents
2. Format the retrieved information in a clear, organized plain text format that another language model can work with
3. Include all relevant facts, steps, and details from the retrieved documents
4. Organize the information logically (e.g., overview, steps, benefits, notes)

CRITICAL RULES:
- ALWAYS call retrieve_documents first to get information
- Format the information clearly and completely - include all relevant details
- Use plain text format, organized with clear sections
- If retrieve_documents returns "No relevant information found in the knowledge base." or similar "no information" messages, you must respond with exactly: "NO_RELEVANT_INFORMATION"
- DO NOT add any information that is not in the retrieved documents
- DO NOT apply any styling, voice, or tone - keep it neutral and factual
- DO NOT simplify or clean the language - just format what you retrieve

Your output will be sent to another language model for cleaning and styling, so make sure all relevant information is included."""
    
    agent = ToolCallingAgent(
        tools=[RetrieveDocumentsTool(retriever=content_retriever)],
        model=model,
        verbosity_level=verbose,
        stream_outputs=False,
        instructions=retrieval_prompt,
    )
    return agent


def _build_language_model(
    style_retriever: StyleRetriever,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
    verbose: int = 1,
) -> ToolCallingAgent:
    """Build the language model (second LLM) that cleans and styles information.
    
    Args:
        style_retriever: ChromaDB retriever for style examples
        audience_level: Target audience level (beginner | intermediate)
        length: Output length preference (short | medium | long)
        energy: Energy level (very_gentle | neutral | slightly_uplifting)
        context: Usage context (sleep | mid-day_reset | pre-work | anxiety_spike | general)
        verbose: Verbosity level for agent output
        
    Returns:
        ToolCallingAgent configured for language cleaning and styling
    """
    model = model_utils.google_build_reasoning_model()
    
    language_prompt = f"""You are the language cleaning and styling model for the Breath app.

Your job:
1. Take the formatted raw information from the retrieval agent
2. Clean and simplify the language
3. Apply the Breath app voice style using retrieved style examples
4. Use ONLY the information provided - do NOT add any new information
5. You can simplify and rephrase, but must keep all factual content

CRITICAL RULES:
- ONLY use information directly from the formatted text provided - NEVER add information
- You can simplify complex language and rephrase for clarity
- You can reorganize information for better flow
- You MUST retrieve style examples using retrieve_style to guide your voice
- Apply the style consistently throughout

Tone (Breath app voice):
- Warm, grounded, calm, not hype
- Talk directly to one person: "you", never "users" or "people"
- Gentle permission language: "you might", "you can", "it's okay if"
- Avoid: "you must", "you should", "you have to"

Language:
- Short sentences, mostly 8–14 words
- Use concrete sensations instead of abstract terms
  - Prefer: "the feeling of your chest rising" over "improved regulation"
- Avoid clinical or techy words:
  - Avoid: "optimize", "intervention", "protocol", "metric"
  - Prefer: "practice", "rhythm", "moment", "body", "space"

Safety:
- Never claim to cure or treat any condition
- Use hedging language: "may help", "can support", "you might notice"
- If medical advice is requested, gently encourage professional care

Structure (default output format):
1. 1–2 sentence overview of the exercise in this voice
2. A short, clear step list (3–6 steps)
3. 1-line gentle closing reflection or invitation

Style adaptation (apply these settings):
- Audience: {audience_level}
- Length: {length}
- Energy: {energy}
- Context: {context}

First, retrieve style examples using retrieve_style, then clean and style the provided information."""
    
    agent = ToolCallingAgent(
        tools=[RetrieveStyleTool(retriever=style_retriever)],
        model=model,
        verbosity_level=verbose,
        stream_outputs=False,
        instructions=language_prompt,
    )
    return agent


def run_agent(
    query: str,
    verbose: int = 1,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
) -> str:
    """Run the two-LLM agent pipeline: retrieval → language cleaning/styling.
    
    This is the main entry point that orchestrates the two-pass flow:
    1. Retrieval Agent: Retrieves raw info and formats it
    2. Language Model: Cleans, simplifies, and styles the information
    
    Args:
        query: User query about breathing exercise
        verbose: Verbosity level for agent output
        audience_level: Target audience level (beginner | intermediate)
        length: Output length preference (short | medium | long)
        energy: Energy level (very_gentle | neutral | slightly_uplifting)
        context: Usage context (sleep | mid-day_reset | pre-work | anxiety_spike | general)
        
    Returns:
        Final cleaned and styled output, or error message if no information found
    """
    # Initialize retrievers
    script_dir = Path(__file__).parent
    vector_store_dir = script_dir / "vector_store"
    
    content_retriever = ChromaRetriever(
        persist_directory=vector_store_dir,
        collection_name="breathing_exercises",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        max_results=4,
    )
    
    style_retriever = StyleRetriever(
        persist_directory=vector_store_dir,
        collection_name="breath_style_guides",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        max_results=4,
    )
    
    # Pass 1: Retrieval Agent - Get raw information and format it
    retrieval_agent = _build_retrieval_agent(
        content_retriever=content_retriever,
        verbose=verbose,
    )
    
    formatted_raw_info = retrieval_agent.run(query)
    
    # Check if retrieval found no relevant information
    # The retrieval agent should return "NO_RELEVANT_INFORMATION" if no info found
    # Also check for empty responses or explicit "no information" messages
    formatted_upper = formatted_raw_info.upper().strip()
    if (
        "NO_RELEVANT_INFORMATION" in formatted_upper
        or formatted_raw_info.strip() == ""
        or "no relevant information found" in formatted_upper
        or "no information" in formatted_upper and "knowledge base" in formatted_upper
    ):
        return NO_INFO_MESSAGE
    
    # Pass 2: Language Model - Clean and style the formatted information
    language_model = _build_language_model(
        style_retriever=style_retriever,
        audience_level=audience_level,
        length=length,
        energy=energy,
        context=context,
        verbose=verbose,
    )
    
    # Create prompt for language model with the formatted raw information
    language_prompt = f"""Clean and style the following breathing exercise information in the Breath app voice.

Use retrieve_style to get style examples, then transform this information:

[FORMATTED_RAW_INFORMATION]
{formatted_raw_info}
"""
    
    final_result = language_model.run(language_prompt)
    
    return final_result


# Legacy function for backward compatibility (now just calls run_agent)
def build_agent(
    verbose: int = 1,
    two_pass: bool = False,  # Ignored - always two-pass now
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
) -> ToolCallingAgent:
    """Build a legacy single-agent interface (for backward compatibility).
    
    Note: This function is kept for compatibility but the recommended approach
    is to use run_agent() which implements the two-LLM architecture.
    
    Args:
        verbose: Verbosity level for agent output
        two_pass: Ignored - always uses two-pass architecture now
        audience_level: Target audience level (beginner | intermediate)
        length: Output length preference (short | medium | long)
        energy: Energy level (very_gentle | neutral | slightly_uplifting)
        context: Usage context (sleep | mid-day_reset | pre-work | anxiety_spike | general)
    """
    # For backward compatibility, we'll create a wrapper agent
    # that internally uses the two-LLM architecture
    model = model_utils.google_build_reasoning_model()
    
    script_dir = Path(__file__).parent
    vector_store_dir = script_dir / "vector_store"
    
    content_retriever = ChromaRetriever(
        persist_directory=vector_store_dir,
        collection_name="breathing_exercises",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        max_results=4,
    )
    
    style_retriever = StyleRetriever(
        persist_directory=vector_store_dir,
        collection_name="breath_style_guides",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        max_results=4,
    )
    
    # Create a simple wrapper that uses both tools but delegates to run_agent internally
    # This maintains the interface but uses the new architecture
    tools = [
        RetrieveDocumentsTool(retriever=content_retriever),
        RetrieveStyleTool(retriever=style_retriever),
    ]
    
    system_prompt = f"""You are the voice of the Breath app. Use retrieve_documents and retrieve_style tools to answer questions.

Style settings:
- Audience: {audience_level}
- Length: {length}
- Energy: {energy}
- Context: {context}"""
    
    agent = ToolCallingAgent(
        tools=tools,
        model=model,
        verbosity_level=verbose,
        stream_outputs=False,
        instructions=system_prompt,
    )
    return agent


# Legacy function - now just calls run_agent
def run_two_pass(
    query: str,
    verbose: int = 1,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
) -> str:
    """Run agent in two-pass mode (legacy function - now just calls run_agent).
    
    Args:
        query: User query about breathing exercise
        verbose: Verbosity level
        audience_level: Target audience level
        length: Output length preference
        energy: Energy level
        context: Usage context
        
    Returns:
        Final styled output
    """
    return run_agent(
        query=query,
        verbose=verbose,
        audience_level=audience_level,
        length=length,
        energy=energy,
        context=context,
    )
