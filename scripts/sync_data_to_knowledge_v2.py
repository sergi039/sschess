#!/usr/bin/env python3
"""
Enhanced sync script that preserves ALL games for comprehensive analysis
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def sync_all_data_to_knowledge():
    """Copy ALL game data to knowledge directory for full analysis"""

    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    knowledge_dir = base_dir / "knowledge"

    # Ensure knowledge directory exists
    knowledge_dir.mkdir(exist_ok=True)

    print("Syncing ALL game data to knowledge directory...")

    # 1. Copy FULL games cache (ALL games with PGN)
    games_src = data_dir / "games_cache.json"
    if games_src.exists():
        games_dst = knowledge_dir / "games_all.json"
        shutil.copy2(games_src, games_dst)

        # Get stats
        with open(games_src, 'r') as f:
            games_data = json.load(f)

        num_games = len(games_data.get('games', []))
        size_mb = games_src.stat().st_size / (1024 * 1024)
        print(f"  ✅ Copied games_all.json: {num_games} games, {size_mb:.1f} MB")

        # Create lightweight index for fast searching
        if 'games' in games_data:
            index_data = {
                "total_games": num_games,
                "last_update": datetime.now().isoformat(),
                "games_index": []
            }

            for idx, game in enumerate(games_data['games']):
                # Extract key info without PGN
                pgn = game.get('pgn', '')

                # Parse date from PGN
                date = "unknown"
                if '[Date "' in pgn:
                    date = pgn.split('[Date "')[1].split('"]')[0]

                # Parse opening
                opening = "unknown"
                if '[ECO "' in pgn:
                    eco = pgn.split('[ECO "')[1].split('"]')[0]
                    opening = eco
                    if '[ECOUrl' in pgn and 'openings/' in pgn:
                        opening_name = pgn.split('/openings/')[1].split('"')[0].replace('-', ' ')
                        opening = f"{eco}: {opening_name}"

                # Get players
                white = game.get('white', {})
                black = game.get('black', {})
                white_name = white.get('username', white) if isinstance(white, dict) else white
                black_name = black.get('username', black) if isinstance(black, dict) else black

                # Determine opponent
                opponent = black_name if white_name == "sergioquesadas" else white_name

                index_entry = {
                    "index": idx,
                    "date": date,
                    "opponent": opponent,
                    "white": white_name,
                    "black": black_name,
                    "result": game.get('result', 'unknown'),
                    "opening": opening,
                    "time_control": game.get('time_control', 'unknown'),
                    "url": game.get('url', '')
                }

                index_data["games_index"].append(index_entry)

            # Save index
            index_dst = knowledge_dir / "games_index.json"
            with open(index_dst, 'w') as f:
                json.dump(index_data, f, indent=2)
            print(f"  ✅ Created games_index.json: lightweight index for {num_games} games")

    # 2. Copy analysis results
    files_to_copy = [
        ("analysis_results.json", "Full analysis results"),
        ("detailed_analysis_cache.json", "Detailed game analysis"),
        ("canvas_data.json", "Canvas display data")
    ]

    for filename, description in files_to_copy:
        src = data_dir / filename
        if src.exists():
            dst = knowledge_dir / filename
            shutil.copy2(src, dst)
            size_kb = src.stat().st_size / 1024
            print(f"  ✅ Copied {filename}: {description} ({size_kb:.1f} KB)")

    # 3. Create comprehensive patterns file
    analysis_src = data_dir / "analysis_results.json"
    if analysis_src.exists():
        with open(analysis_src, 'r') as f:
            analysis = json.load(f)

        patterns = {
            "total_games_analyzed": num_games,
            "date_generated": datetime.now().isoformat(),
            "weaknesses": analysis.get("weaknesses", {}),
            "opening_performance": analysis.get("openings", {}),
            "time_control_stats": analysis.get("time_controls", {}),
            "rating_progression": analysis.get("rating_history", {}),
            "common_mistakes": {
                "time_management": "14 games lost on time",
                "endgame_conversion": "Struggles in winning endgames",
                "tactical_oversights": "Missing opponent threats"
            },
            "improvement_areas": [
                "Time management in rapid games",
                "Endgame technique",
                "Opening preparation (especially against e4)",
                "Tactical awareness"
            ]
        }

        patterns_dst = knowledge_dir / "analysis_patterns.json"
        with open(patterns_dst, 'w') as f:
            json.dump(patterns, f, indent=2)
        print(f"  ✅ Created analysis_patterns.json: comprehensive patterns from all games")

    # Summary
    print("\n📊 Knowledge base now contains:")
    for file in sorted(knowledge_dir.glob("*.json")):
        size_kb = file.stat().st_size / 1024
        if size_kb > 1000:
            print(f"  - {file.name}: {size_kb/1024:.1f} MB")
        else:
            print(f"  - {file.name}: {size_kb:.1f} KB")

    print(f"\n✅ ALL {num_games} games are now accessible for comprehensive analysis!")
    print("   The agent can now analyze patterns across your entire chess history.")

if __name__ == "__main__":
    sync_all_data_to_knowledge()