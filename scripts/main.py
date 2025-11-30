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
from lichess_analyzer import LichessAnalyzer
from tactical_detector import TacticalDetector
from opening_database import OpeningDatabase
from study_generator import StudyGenerator
from generate_lichess_markdown import LichessMarkdownGenerator


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


def run_pipeline(username: str, months_back: int = None, skip_fetch: bool = False,
                 enable_lichess: bool = False):
    """
    Run the complete analysis pipeline.

    Args:
        username: Chess.com username
        months_back: Number of months to fetch (None = all)
        skip_fetch: Skip fetching new games (use existing cache)
        enable_lichess: Enable Lichess analysis (default: False)

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

        # Step 3: Lichess Analysis (only if explicitly enabled)
        lichess_analysis = None
        tactical_analysis = None
        opening_analysis = None
        study_urls = []

        if enable_lichess:
            lichess_token = os.environ.get("LICHESS_TOKEN")
            if lichess_token:
                print("\n♟️ STEP 3: LICHESS ANALYSIS")
                print("-" * 40)

                try:
                    # Load games for Lichess analysis
                    import json
                    with open("data/games_cache.json", 'r') as f:
                        games_data = json.load(f)
                    games = games_data.get("games", [])[:5]  # Analyze only last 5 games for speed

                    # 3a. Computer Analysis (simplified for GitHub Actions)
                    print("  Running simplified analysis...")
                    lichess_analyzer = LichessAnalyzer(lichess_token)
                    lichess_analysis = lichess_analyzer.analyze_multiple_games(games)
                    print(f"  ✅ Analyzed {lichess_analysis.get('games_analyzed', 0)} games")
                    print(f"  📊 Average accuracy: {lichess_analysis.get('average_accuracy', 0)}%")

                    # 3b. Tactical Pattern Detection
                    print("\n  Detecting tactical patterns...")
                    tactical_detector = TacticalDetector()
                    tactical_analysis = tactical_detector.analyze_multiple_games_tactics(games)
                    print(f"  ✅ Found {tactical_analysis.get('total_tactics_found', 0)} tactical patterns")

                    # 3c. Opening Database Analysis
                    print("\n  Analyzing opening repertoire...")
                    opening_db = OpeningDatabase(lichess_token)
                    opening_analysis = opening_db.analyze_player_openings(games, username)
                    print(f"  ✅ Analyzed {len(opening_analysis.get('opening_analysis', []))} opening variations")

                    # 3d. Generate Lichess Study
                    print("\n  Creating Lichess studies...")
                    study_gen = StudyGenerator(lichess_token)

                    # Create opening study
                    opening_study = study_gen.create_opening_study(username, games, opening_analysis)
                    if opening_study:
                        study_urls.append(opening_study)
                        print(f"  ✅ Created opening study: {opening_study}")

                    # Create improvement study
                    if lichess_analysis and lichess_analysis.get("games_analysis"):
                        recommendations = lichess_analyzer.generate_improvement_recommendations(lichess_analysis)
                        improvement_study = study_gen.create_improvement_study(
                            username,
                            lichess_analysis["games_analysis"],
                            recommendations
                        )
                        if improvement_study:
                            study_urls.append(improvement_study)
                            print(f"  ✅ Created improvement study: {improvement_study}")

                except Exception as e:
                    print(f"  ⚠️ Lichess analysis error: {e}")
                    # Continue without Lichess analysis
            else:
                print("\n⏭️  STEP 3: SKIPPING LICHESS ANALYSIS (no token found)")
                print("      To enable: Add LICHESS_TOKEN to .env and use --enable-lichess flag")
        else:
            print("\n⏭️  STEP 3: SKIPPING LICHESS ANALYSIS (not requested)")
            print("      To enable: Use --enable-lichess flag")

        # Step 4: Generate Markdown
        print("\n📝 STEP 4: GENERATING DOCUMENTATION")
        print("-" * 40)
        generator = MarkdownGenerator()
        generator.generate_all()
        files_generated = 4

        # Generate Lichess markdown if analysis was done
        if lichess_analysis or tactical_analysis or opening_analysis:
            lichess_generator = LichessMarkdownGenerator()
            lichess_generator.generate_all(
                lichess_analysis,
                tactical_analysis,
                opening_analysis,
                study_urls
            )
            files_generated += 6  # Lichess adds 6 more files

        print(f"✅ Generated {files_generated} Markdown files")

        # Summary
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print("\n📁 Generated files:")
        print("   - knowledge/summary.md")
        print("   - knowledge/openings.md")
        print("   - knowledge/weaknesses.md")
        print("   - knowledge/recent_games.md")

        if lichess_analysis or tactical_analysis or opening_analysis:
            print("\n📊 Lichess Analysis files:")
            print("   - knowledge/lichess_accuracy.md")
            print("   - knowledge/lichess_mistakes.md")
            print("   - knowledge/lichess_tactics.md")
            print("   - knowledge/lichess_openings.md")
            print("   - knowledge/lichess_improvement.md")
            print("   - knowledge/lichess_studies.md")

        print("\n💾 Data files:")
        print("   - data/games_cache.json")
        print("   - data/analysis_results.json")
        if lichess_analysis:
            print("   - data/lichess_analysis_cache.json")

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
    parser.add_argument(
        "--enable-lichess",
        action="store_true",
        help="Enable Lichess analysis (computer analysis, tactics, etc.)"
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
    success = run_pipeline(username, months, args.skip_fetch, args.enable_lichess)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()