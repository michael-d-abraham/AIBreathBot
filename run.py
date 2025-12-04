#!/usr/bin/env python3
"""Entry point for the Breathing Exercise Agent."""

import sys
import argparse
from agent import run_agent


def print_usage():
    """Print usage information."""
    print("Setup (first time only):")
    print("  python ingest_exercises.py")
    print("  python ingest_style.py")
    print("\nUsage:")
    print("  python run.py \"<your question>\"")
    print("  python run.py --chat")
    print("\nExamples:")
    print("  python run.py \"How do I do 4-7-8 breathing?\"")
    print("  python run.py \"Create me a short description for deep breathing\"")
    print("  python run.py \"What are the benefits of box breathing?\"")
    print("\nStyle Keywords:")
    print("  - shortDescription: 6-12 word summary")
    print("  - description: 2-4 sentence explanation")
    print("  - benefit: list of benefits")
    print("  - method: step-by-step instructions")

    


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
    try:
        result = run_agent(
            query=query,
            verbose=0,
            audience_level=audience_level,
            length=length,
            energy=energy,
            context=context,
        )
        print(result)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            print(f"Rate limit error. Please wait a few minutes and try again.")
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
    print("Ask questions about breathing exercises. Type 'exit' to quit.\n")
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            if not question:
                continue
            
            try:
                result = run_agent(
                    query=question,
                    verbose=0,
                    audience_level=audience_level,
                    length=length,
                    energy=energy,
                    context=context,
                )
                print(f"\n{result}\n")
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    print("Rate limit error. Please wait and try again.\n")
                else:
                    print(f"Error: {error_msg}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                print("Rate limit error. Please wait and try again.\n")
            else:
                print(f"Error: {error_msg}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Breathing Exercise Chatbot",
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
