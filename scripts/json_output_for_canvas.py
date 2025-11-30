#!/usr/bin/env python3
"""
Generate JSON output for TypingMind Interactive Canvas.

This module prepares chess game data in JSON format that can be used
by Claude in TypingMind to generate an Interactive Canvas with chess board.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ChessDataForCanvas:
    """Prepare chess data for Interactive Canvas rendering."""

    def __init__(self):
        """Initialize the data processor."""
        self.cache_dir = Path("data")
        self.games_cache = self.cache_dir / "games_cache.json"
        self.analysis_cache = self.cache_dir / "detailed_analysis_cache.json"

    def load_game_and_analysis(self, query: str) -> tuple[Optional[Dict], Optional[Dict]]:
        """
        Load game and its analysis by query.

        Args:
            query: Search query (date, opponent, or URL)

        Returns:
            Tuple of (game_data, analysis_data) or (None, None) if not found
        """
        # Load games
        if not self.games_cache.exists():
            return None, None

        with open(self.games_cache, 'r') as f:
            data = json.load(f)
            games = data.get("games", [])

        # Find game
        game = None
        query_lower = query.lower()

        for g in games:
            game_date = datetime.fromtimestamp(g.get("end_time", 0))
            date_str = game_date.strftime("%Y-%m-%d")

            if query_lower in date_str.lower():
                game = g
                break

            # Check players
            white = g.get("white", {}).get("username", "").lower()
            black = g.get("black", {}).get("username", "").lower()
            if query_lower in white or query_lower in black:
                game = g
                break

            # Check URL
            if query_lower in g.get("url", "").lower():
                game = g
                break

        if not game:
            return None, None

        # Load analysis if exists
        analysis = None
        if self.analysis_cache.exists():
            with open(self.analysis_cache, 'r') as f:
                cached = json.load(f)
                game_id = game.get("url", "")
                if game_id in cached:
                    analysis = cached[game_id]

        return game, analysis

    def prepare_canvas_data(self, game: Dict, analysis: Optional[Dict] = None) -> Dict:
        """
        Prepare data in format optimized for Interactive Canvas.

        Args:
            game: Game data from Chess.com
            analysis: Optional Stockfish analysis

        Returns:
            JSON-serializable dict with all necessary data for canvas
        """
        white = game.get("white", {})
        black = game.get("black", {})

        # Basic game info
        canvas_data = {
            "game_info": {
                "white_player": white.get("username", "White"),
                "black_player": black.get("username", "Black"),
                "white_rating": white.get("rating", "?"),
                "black_rating": black.get("rating", "?"),
                "result": self._format_result(white.get("result", "")),
                "date": datetime.fromtimestamp(game.get("end_time", 0)).strftime("%Y-%m-%d %H:%M"),
                "time_control": game.get("time_control", ""),
                "url": game.get("url", "")
            },
            "pgn": game.get("pgn", ""),
            "eco": {
                "code": game.get("eco", ""),
                "name": game.get("eco_url", "").split("/")[-1].replace("-", " ").title() if game.get("eco_url") else ""
            }
        }

        # Add analysis if available
        if analysis:
            canvas_data["analysis"] = {
                "accuracy": analysis.get("accuracy", 0),
                "total_moves": analysis.get("total_moves", 0),
                "blunders": analysis.get("blunders", 0),
                "mistakes": analysis.get("mistakes", 0),
                "inaccuracies": analysis.get("inaccuracies", 0),
                "good_moves": analysis.get("good_moves", 0),
                "engine_depth": analysis.get("engine_depth", 20)
            }

            # Add move-by-move analysis
            if analysis.get("analysis"):
                moves_analysis = []
                for move_data in analysis["analysis"]:
                    moves_analysis.append({
                        "move": move_data.get("move", ""),
                        "move_number": move_data.get("move_number", 0),
                        "eval_before": move_data.get("eval_before", 0),
                        "eval_after": move_data.get("eval_after", 0),
                        "eval_loss": move_data.get("eval_loss", 0),
                        "classification": move_data.get("classification", ""),
                        "best_move": move_data.get("best_move", "")
                    })
                canvas_data["moves_analysis"] = moves_analysis

                # Extract critical moments
                critical_moves = [
                    m for m in moves_analysis
                    if m["classification"] in ["blunder", "mistake", "brilliant"]
                ]
                canvas_data["critical_moments"] = critical_moves[:5]

        # Add instructions for Interactive Canvas
        canvas_data["canvas_instructions"] = {
            "type": "chess_board",
            "viewer": "lichess-pgn-viewer",
            "features": [
                "interactive_board",
                "move_navigation",
                "analysis_display",
                "evaluation_bar"
            ],
            "cdn_urls": {
                "css": "https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css",
                "js": "https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"
            }
        }

        return canvas_data

    def _format_result(self, result: str) -> str:
        """Format game result."""
        if result == "win":
            return "1-0"
        elif result in ["checkmated", "resigned", "timeout", "abandoned"]:
            return "0-1"
        elif result in ["agreed", "repetition", "stalemate", "insufficient", "50move"]:
            return "½-½"
        else:
            return "*"

    def generate_json_response(self, query: str) -> str:
        """
        Generate JSON response for a game query.

        Args:
            query: Search query for the game

        Returns:
            JSON string with game data or error message
        """
        game, analysis = self.load_game_and_analysis(query)

        if not game:
            return json.dumps({
                "error": f"Game not found for query: '{query}'",
                "suggestions": [
                    "Try searching by date (e.g., '2025-11-29')",
                    "Try searching by opponent name",
                    "Try using the game URL"
                ]
            }, indent=2)

        canvas_data = self.prepare_canvas_data(game, analysis)
        return json.dumps(canvas_data, indent=2)


def main():
    """Test the JSON output generator."""
    import sys

    if len(sys.argv) < 2:
        query = "2025-11-29"  # Default test query
    else:
        query = " ".join(sys.argv[1:])

    processor = ChessDataForCanvas()
    json_output = processor.generate_json_response(query)

    print(json_output)

    # Save to file
    output_file = Path("data/canvas_data.json")
    with open(output_file, 'w') as f:
        f.write(json_output)

    print(f"\n\nJSON data saved to: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()