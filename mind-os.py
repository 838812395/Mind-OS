import sys
import argparse
from scripts.consistency_check import scan_system
from scripts.radar_gen import create_radar_chart
from scripts.memory_engine import sync_memory, query_memory

def main():
    parser = argparse.ArgumentParser(description="Mind-OS CLI - Your Psyche's Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit command
    subparsers.add_parser("audit", help="Scan system for logical gaps and metadata issues")

    # Viz command
    subparsers.add_parser("viz", help="Generate 5D Ability Radar chart")

    # Memory Sync command
    subparsers.add_parser("sync", help="Sync local notes into semantic memory (LlamaIndex)")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query semantic memory")
    query_parser.add_argument("text", type=str, help="The query text")

    # Capture command
    capture_parser = subparsers.add_parser("capture", help="Quickly log a thought or insight")
    capture_parser.add_argument("message", type=str, help="The thought to record")

    args = parser.parse_args()

    if args.command == "audit":
        scan_system(".")
    elif args.command == "viz":
        create_radar_chart()
    elif args.command == "sync":
        sync_memory()
    elif args.command == "query":
        query_memory(args.text)
    elif args.command == "capture":
        print(f"📝 Thought captured: '{args.message}'")
        print("(Integration with journal files coming in next update)")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
