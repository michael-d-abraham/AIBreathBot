#!/usr/bin/env python3
"""Entry point for the Breathing Exercise Agent."""

import sys
from agent import build_agent


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
    print("\nExamples:")
    print("  Single question:")
    print("    python run.py \"How do I do 4-7-8 breathing?\"")
    print("    python run.py \"What are the benefits of breathing exercises?\"")
    print("\n  Interactive chat:")
    print("    python run.py --chat")
    print("    (then ask multiple questions in a conversation)")
    print("\nNote: Make sure to run 'python ingest_exercises.py' first to")
    print("      populate the knowledge base with breathing exercise content.")


def run_single_question(query: str):
    """Run the agent for a single question."""
    print(f"\n{'='*60}")
    print("Breathing Exercise Chatbot")
    print(f"{'='*60}")
    print(f"\nQuery: {query}\n")
    
    agent = build_agent(verbose=2)
    result = agent.run(query)
    
    print(f"\n{'='*60}")
    print("=== Answer ===")
    print(f"{'='*60}")
    print(result)


def run_interactive_chat():
    """Run the agent in interactive chat mode."""
    print(f"\n{'='*60}")
    print("Breathing Exercise Chatbot - Interactive Mode")
    print(f"{'='*60}")
    print("\nAsk questions about breathing exercises from the knowledge base.")
    print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.\n")
    
    agent = build_agent(verbose=1)
    
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
            result = agent.run(question)
            print(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Take care of your breathing!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try asking another question.")


def main():
    """Main entry point."""
    # No arguments - default to interactive chat mode
    if len(sys.argv) == 1:
        run_interactive_chat()
        return
    
    # Check for flags
    first_arg = sys.argv[1]
    
    # Help flag
    if first_arg in ["-h", "--help", "help"]:
        print_usage()
        return
    
    # Interactive chat mode
    if first_arg in ["--chat", "-c", "--interactive", "-i"]:
        run_interactive_chat()
        return
    
    # Single question mode - treat first argument as the question
    query = first_arg
    run_single_question(query)


if __name__ == "__main__":
    main()
