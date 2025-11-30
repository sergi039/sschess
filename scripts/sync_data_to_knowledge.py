#!/usr/bin/env python3
"""
Syncs game data from data/ directory to knowledge/ directory for TypingMind access
"""

import json
import shutil
from pathlib import Path

def sync_data_to_knowledge():
    """Copy essential data files to knowledge directory for TypingMind access"""

    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    knowledge_dir = base_dir / "knowledge"

    # Ensure knowledge directory exists
    knowledge_dir.mkdir(exist_ok=True)

    # Files to sync
    files_to_sync = [
        "games_cache.json",
        "analysis_results.json",
        "detailed_analysis_cache.json",
        "canvas_data.json"
    ]

    print("Syncing data files to knowledge directory...")

    for filename in files_to_sync:
        src = data_dir / filename
        dst = knowledge_dir / filename

        if src.exists():
            # For large files like games_cache, create a summary version
            if filename == "games_cache.json" and src.stat().st_size > 500000:
                print(f"Creating summary version of {filename}...")
                with open(src, 'r') as f:
                    data = json.load(f)

                # For games_cache, we need to preserve the structure
                if 'games' in data:
                    # Keep the structure but limit games to last 50
                    summary_data = {
                        'username': data.get('username'),
                        'last_update': data.get('last_update'),
                        'games': data['games'][-50:] if isinstance(data['games'], list) else data['games'],
                        'archives_fetched': data.get('archives_fetched')
                    }
                else:
                    # For list format, take last 50
                    summary_data = data[-50:] if isinstance(data, list) else data

                # Save as summary file
                summary_dst = knowledge_dir / "games_summary.json"
                with open(summary_dst, 'w') as f:
                    json.dump(summary_data, f, indent=2)
                print(f"  Created {summary_dst.name} with last 50 games")

                # Also create a metadata file
                total_games = len(data['games']) if 'games' in data else (len(data) if isinstance(data, list) else 0)
                metadata = {
                    "total_games": total_games,
                    "summary_games": min(50, total_games),
                    "last_update": str(src.stat().st_mtime),
                    "full_data_location": "data/games_cache.json",
                    "note": "games_summary.json contains last 50 games only"
                }
                metadata_dst = knowledge_dir / "games_metadata.json"
                with open(metadata_dst, 'w') as f:
                    json.dump(metadata, f, indent=2)
                print(f"  Created {metadata_dst.name}")

            else:
                # Copy smaller files directly
                shutil.copy2(src, dst)
                print(f"  Copied {filename}")
        else:
            print(f"  Warning: {filename} not found in data directory")

    print("\nSync complete! Knowledge directory now contains:")
    for file in sorted(knowledge_dir.glob("*.json")):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    sync_data_to_knowledge()