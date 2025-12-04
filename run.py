#!/usr/bin/env python3
"""Entry point for the Breathing Exercise Agent."""

import sys
import argparse
from agent import run_agent


def print_usage():
    """Print usage information."""
    print("Breathing Exercise Chatbot")
    print("=" * 60)
    print("\nUsage:")
    print("  1. Single Question Mode:")
    print("     python run.py \"<your question>\"")
    print("\n  2. Interactive Chat Mode:")
    print("     python run.py")
    print("     python run.py --chat")
    print("\nOptions:")
    print("  --audience-level LEVEL   Target audience (beginner | intermediate)")
    print("  --length LENGTH         Output length (short | medium | long)")
    print("  --energy ENERGY         Energy level (very_gentle | neutral | slightly_uplifting)")
    print("  --context CONTEXT       Usage context (sleep | mid-day_reset | pre-work | anxiety_spike | general)")
    print("\nNote: The system always uses a two-pass architecture:")
    print("      1. Retrieval Agent: Retrieves and formats raw information")
    print("      2. Language Model: Cleans and styles the information")
    print("\nExamples:")
    print("  Single question:")
    print("    python run.py \"How do I do 4-7-8 breathing?\"")
    print("    python run.py \"What are the benefits?\"")
    print("    python run.py \"Describe box breathing\" --audience-level intermediate --energy neutral")
    print("\n  Interactive chat:")
    print("    python run.py --chat")
    print("    (then ask multiple questions in a conversation)")
    print("\nNote: Make sure to run 'python ingest_exercises.py' first to")
    print("      populate the knowledge base with breathing exercise content.")
    print("      Also run 'python ingest_style.py' to populate style examples.")


def run_single_question(
    query: str,
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
):
    """Run the agent for a single question.
    
    Args:
        query: User question
        audience_level: Target audience level
        length: Output length preference
        energy: Energy level
        context: Usage context
    """
    print(f"\n{'='*60}")
    print("Breathing Exercise Chatbot")
    print(f"{'='*60}")
    print(f"\nQuery: {query}\n")
    print("Mode: Two-pass (Retrieval Agent → Language Model)\n")
    
    try:
        result = run_agent(
            query=query,
            verbose=2,
            audience_level=audience_level,
            length=length,
            energy=energy,
            context=context,
        )
        
        print(f"\n{'='*60}")
        print("=== Answer ===")
        print(f"{'='*60}")
        print(result)
    except Exception as e:
        error_msg = str(e)
        print(f"\n{'='*60}")
        print("=== Error ===")
        print(f"{'='*60}")
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            print(f"Rate limit error: {error_msg[:300]}")
            print("\n💡 Tip: You've hit your API quota limit. Please:")
            print("   - Wait a few minutes before trying again")
            print("   - Check your API usage at https://ai.dev/usage")
            print("   - Consider upgrading your plan if needed")
        else:
            print(f"Error: {error_msg}")


def run_interactive_chat(
    audience_level: str = "beginner",
    length: str = "medium",
    energy: str = "very_gentle",
    context: str = "general",
):
    """Run the agent in interactive chat mode.
    
    Args:
        audience_level: Target audience level
        length: Output length preference
        energy: Energy level
        context: Usage context
    """
    print(f"\n{'='*60}")
    print("Breathing Exercise Chatbot - Interactive Mode")
    print(f"{'='*60}")
    print("\nAsk questions about breathing exercises from the knowledge base.")
    print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.\n")
    print("Mode: Two-pass (Retrieval Agent → Language Model)")
    print(f"Settings: audience={audience_level}, length={length}, energy={energy}, context={context}\n")
    
    while True:
        try:
            # Get user input
            question = input("\n🫁 You: ").strip()
            
            # Check for exit commands
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! Take care of your breathing!")
                break
            
            # Skip empty inputs
            if not question:
                continue
            
            # Run the agent
            print("\n🤖 Chatbot: ", end="", flush=True)
            try:
                result = run_agent(
                    query=question,
                    verbose=1,
                    audience_level=audience_level,
                    length=length,
                    energy=energy,
                    context=context,
                )
                print(result)
            except Exception as e:
                error_msg = str(e)
                # Check for rate limit errors
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    print(f"\n❌ Rate limit error: {error_msg[:200]}")
                    print("\n💡 Tip: You've hit your API quota limit. Please:")
                    print("   - Wait a few minutes before trying again")
                    print("   - Check your API usage at https://ai.dev/usage")
                    print("   - Consider upgrading your plan if needed")
                else:
                    print(f"\n❌ Error: {error_msg}")
                    print("Please try asking another question.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Take care of your breathing!")
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                print(f"\n❌ Rate limit error: {error_msg[:200]}")
                print("\n💡 Tip: You've hit your API quota limit. Please wait before trying again.")
            else:
                print(f"\n❌ Error: {error_msg}")
                print("Please try asking another question.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Breathing Exercise Content Generator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, starts interactive mode)",
    )
    parser.add_argument(
        "--chat",
        "-c",
        dest="interactive",
        action="store_true",
        help="Start interactive chat mode",
    )
    parser.add_argument(
        "--audience-level",
        choices=["beginner", "intermediate"],
        default="beginner",
        help="Target audience level (default: beginner)",
    )
    parser.add_argument(
        "--length",
        choices=["short", "medium", "long"],
        default="medium",
        help="Output length preference (default: medium)",
    )
    parser.add_argument(
        "--energy",
        choices=["very_gentle", "neutral", "slightly_uplifting"],
        default="very_gentle",
        help="Energy level (default: very_gentle)",
    )
    parser.add_argument(
        "--context",
        choices=["sleep", "mid-day_reset", "pre-work", "anxiety_spike", "general"],
        default="general",
        help="Usage context (default: general)",
    )
    
    args = parser.parse_args()
    
    # Help flag
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help", "help"]):
        print_usage()
        return
    
    # Extract parameters
    audience_level = args.audience_level
    length = args.length
    energy = args.energy
    context = args.context
    
    # Interactive mode
    if args.interactive or not args.query:
        run_interactive_chat(
            audience_level=audience_level,
            length=length,
            energy=energy,
            context=context,
        )
        return
    
    # Single question mode
    run_single_question(
        query=args.query,
        audience_level=audience_level,
        length=length,
        energy=energy,
        context=context,
    )


if __name__ == "__main__":
    main()
