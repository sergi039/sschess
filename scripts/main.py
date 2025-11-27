#!/usr/bin/env python3
"""
Main orchestrator script for Chess Knowledge Base.

This script runs the complete pipeline:
1. Fetch games from Chess.com
2. Analyze games for patterns
3. Generate Markdown documentation

Can be run locally or via GitHub Actions.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fetch_games import ChessComFetcher
from analyze import ChessAnalyzer
from generate_markdown import MarkdownGenerator


def load_env():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("Loading .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


def run_pipeline(username: str, months_back: int = None, skip_fetch: bool = False):
    """
    Run the complete analysis pipeline.

    Args:
        username: Chess.com username
        months_back: Number of months to fetch (None = all)
        skip_fetch: Skip fetching new games (use existing cache)

    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("CHESS KNOWLEDGE BASE PIPELINE")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    try:
        # Step 1: Fetch games
        if not skip_fetch:
            print("\n📥 STEP 1: FETCHING GAMES")
            print("-" * 40)
            fetcher = ChessComFetcher(username)

            # Fetch player profile
            profile = fetcher.fetch_player_profile()
            if profile:
                print(f"✅ Found player: {profile.get('name', username)}")

            # Fetch games
            new_games = fetcher.fetch_games(months_back)
            print(f"✅ Fetched {new_games} new games")

            # Show summary
            summary = fetcher.get_summary()
            print(f"📊 Total games in cache: {summary['total_games']}")
        else:
            print("\n⏭️  STEP 1: SKIPPING FETCH (using existing cache)")

        # Check if cache exists
        cache_file = Path("data/games_cache.json")
        if not cache_file.exists():
            print("❌ Error: No games cache found. Cannot proceed without data.")
            return False

        # Step 2: Analyze games
        print("\n🔍 STEP 2: ANALYZING GAMES")
        print("-" * 40)
        analyzer = ChessAnalyzer()
        analysis = analyzer.generate_analysis()
        print(f"✅ Analysis complete")

        # Show key insights
        weaknesses = analysis.get("weaknesses", {}).get("identified_weaknesses", [])
        if weaknesses:
            print(f"⚠️  Found {len(weaknesses)} areas for improvement")

        ratings = analysis.get("rating_progress", {}).get("current_ratings", {})
        if ratings:
            print(f"📈 Current ratings: {', '.join(f'{k}:{v}' for k, v in ratings.items())}")

        # Step 3: Generate Markdown
        print("\n📝 STEP 3: GENERATING DOCUMENTATION")
        print("-" * 40)
        generator = MarkdownGenerator()
        generator.generate_all()
        print(f"✅ Generated 4 Markdown files")

        # Summary
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print("\n📁 Generated files:")
        print("   - knowledge/summary.md")
        print("   - knowledge/openings.md")
        print("   - knowledge/weaknesses.md")
        print("   - knowledge/recent_games.md")
        print("\n📊 Data files:")
        print("   - data/games_cache.json")
        print("   - data/analysis_results.json")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chess Knowledge Base Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with environment variables
  python main.py

  # Specify username directly
  python main.py --username MyChessUsername

  # Fetch only last 6 months
  python main.py --username MyChessUsername --months 6

  # Skip fetching, just analyze existing cache
  python main.py --username MyChessUsername --skip-fetch

Environment variables:
  CHESS_USERNAME - Chess.com username
  MONTHS_TO_FETCH - Number of months to fetch (optional)
        """
    )

    parser.add_argument(
        "--username",
        help="Chess.com username (overrides CHESS_USERNAME env var)"
    )
    parser.add_argument(
        "--months",
        type=int,
        help="Number of months to fetch (default: all)"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip fetching new games, use existing cache"
    )

    args = parser.parse_args()

    # Load environment variables
    load_env()

    # Get username
    username = args.username or os.environ.get("CHESS_USERNAME")
    if not username:
        print("Error: No username provided!")
        print("Set CHESS_USERNAME in .env file or use --username flag")
        sys.exit(1)

    # Get months to fetch
    months = args.months
    if not months:
        env_months = os.environ.get("MONTHS_TO_FETCH")
        months = int(env_months) if env_months else None

    # Run pipeline
    success = run_pipeline(username, months, args.skip_fetch)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()