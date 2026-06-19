from pathlib import Path
from smolagents import ToolCallingAgent
import model_utils
from tools.retrieval_tool import RetrieveDocumentsTool, RetrieveStyleTool
from tools.vector_store import ChromaRetriever, StyleRetriever

NO_INFO_MESSAGE = "I don't have that information in my knowledge base at the moment."


def _build_retrieval_agent(
    content_retriever: ChromaRetriever,
    verbose: int = 1,
) -> ToolCallingAgent:
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
    
    retrieval_agent = _build_retrieval_agent(
        content_retriever=content_retriever,
        verbose=verbose,
    )
    
    formatted_raw_info = retrieval_agent.run(query)
    
    formatted_upper = formatted_raw_info.upper().strip()
    if (
        "NO_RELEVANT_INFORMATION" in formatted_upper
        or formatted_raw_info.strip() == ""
        or "no relevant information found" in formatted_upper
        or "no information" in formatted_upper and "knowledge base" in formatted_upper
    ):
        return NO_INFO_MESSAGE
    
    language_model = _build_language_model(
        style_retriever=style_retriever,
        audience_level=audience_level,
        length=length,
        energy=energy,
        context=context,
        verbose=verbose,
    )
    
    language_prompt = f"""Clean and style the following breathing exercise information in the Breath app voice.

Use retrieve_style to get style examples, then transform this information:

[FORMATTED_RAW_INFORMATION]
{formatted_raw_info}
"""
    
    final_result = language_model.run(language_prompt)
    
    return final_result


def build_agent(
    verbose: int = 1,
    two_pass: bool = False,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
) -> ToolCallingAgent:
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


def run_two_pass(
    query: str,
    verbose: int = 1,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
) -> str:
    return run_agent(
        query=query,
        verbose=verbose,
        audience_level=audience_level,
        length=length,
        energy=energy,
        context=context,
    )
