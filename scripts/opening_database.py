#!/usr/bin/env python3
"""
Opening database integration with Lichess.

This module provides opening analysis, statistics, and recommendations
based on Lichess's massive game database.
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path


class OpeningDatabase:
    """Interface with Lichess opening database."""

    def __init__(self, token: str = None, cache_dir: str = "data"):
        """
        Initialize opening database.

        Args:
            token: Optional Lichess API token
            cache_dir: Directory for caching opening data
        """
        self.token = token
        self.headers = {}
        if token:
            self.headers = {"Authorization": f"Bearer {token}"}

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.opening_cache_file = self.cache_dir / "opening_database.json"
        self.opening_cache = self._load_opening_cache()

    def _load_opening_cache(self) -> Dict:
        """Load cached opening data."""
        if self.opening_cache_file.exists():
            with open(self.opening_cache_file, 'r') as f:
                return json.load(f)
        return {
            "openings": {},
            "last_update": None
        }

    def _save_opening_cache(self):
        """Save opening cache to disk."""
        with open(self.opening_cache_file, 'w') as f:
            json.dump(self.opening_cache, f, indent=2)

    def get_opening_stats(self, moves: str, rating: int = 1500) -> Optional[Dict]:
        """
        Get statistics for a specific opening position.

        Args:
            moves: Space-separated move list (e.g., "e2e4 e7e5 g1f3")
            rating: Rating range to query (1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500)

        Returns:
            Opening statistics from Lichess database
        """
        cache_key = f"{moves}_{rating}"

        # Check cache first
        if cache_key in self.opening_cache.get("openings", {}):
            return self.opening_cache["openings"][cache_key]

        # Query Lichess opening explorer
        url = "https://explorer.lichess.ovh/lichess"
        params = {
            "variant": "standard",
            "speeds": "blitz,rapid,classical",
            "ratings": str(rating),
            "moves": moves
        }

        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Process the data
            stats = self._process_opening_data(data, moves)

            # Cache the result
            self.opening_cache["openings"][cache_key] = stats
            self._save_opening_cache()

            # Rate limiting
            time.sleep(0.3)

            return stats

        except requests.exceptions.RequestException as e:
            print(f"Error querying opening database: {e}")
            return None

    def _process_opening_data(self, data: Dict, moves: str) -> Dict:
        """
        Process raw opening data from Lichess.

        Args:
            data: Raw response from Lichess API
            moves: The move sequence

        Returns:
            Processed opening statistics
        """
        total_games = data.get("white", 0) + data.get("draws", 0) + data.get("black", 0)

        if total_games == 0:
            return {
                "position": moves,
                "total_games": 0,
                "statistics": {},
                "top_moves": [],
                "opening_name": data.get("opening", {}).get("name", "Unknown")
            }

        # Calculate win percentages
        white_wins = data.get("white", 0)
        draws = data.get("draws", 0)
        black_wins = data.get("black", 0)

        statistics = {
            "white_win_rate": round(white_wins / total_games * 100, 1),
            "draw_rate": round(draws / total_games * 100, 1),
            "black_win_rate": round(black_wins / total_games * 100, 1),
            "total_games": total_games,
            "average_rating": data.get("averageRating", 0)
        }

        # Get top moves from this position
        top_moves = []
        for move_data in data.get("moves", [])[:5]:  # Top 5 moves
            move_stats = {
                "move": move_data.get("san", ""),
                "uci": move_data.get("uci", ""),
                "games": move_data.get("white", 0) + move_data.get("draws", 0) + move_data.get("black", 0),
                "white_win_rate": round(move_data.get("white", 0) / max(1, move_data.get("white", 0) +
                                                                       move_data.get("draws", 0) +
                                                                       move_data.get("black", 0)) * 100, 1),
                "average_rating": move_data.get("averageRating", 0)
            }
            top_moves.append(move_stats)

        # Get recent games
        recent_games = []
        for game in data.get("recentGames", [])[:3]:
            recent_games.append({
                "id": game.get("id", ""),
                "winner": game.get("winner", "draw"),
                "white_rating": game.get("white", {}).get("rating", 0),
                "black_rating": game.get("black", {}).get("rating", 0)
            })

        # Get opening name and ECO
        opening_info = data.get("opening", {})

        return {
            "position": moves,
            "opening_name": opening_info.get("name", "Unknown"),
            "eco": opening_info.get("eco", ""),
            "statistics": statistics,
            "top_moves": top_moves,
            "recent_games": recent_games,
            "opening_family": self._get_opening_family(opening_info.get("name", ""))
        }

    def _get_opening_family(self, opening_name: str) -> str:
        """Categorize opening into families."""
        families = {
            "King's Pawn": ["e4", "King's Pawn", "Italian", "Spanish", "Scotch", "French", "Caro-Kann",
                           "Sicilian", "Pirc", "Alekhine", "Scandinavian"],
            "Queen's Pawn": ["d4", "Queen's Pawn", "Queen's Gambit", "King's Indian", "Nimzo-Indian",
                            "Queen's Indian", "Benoni", "Dutch", "Grünfeld"],
            "English": ["English", "c4"],
            "Reti": ["Réti", "Nf3", "King's Indian Attack"],
            "Other": []
        }

        for family, keywords in families.items():
            for keyword in keywords:
                if keyword.lower() in opening_name.lower():
                    return family

        return "Other"

    def analyze_player_openings(self, games: List[Dict], username: str) -> Dict:
        """
        Analyze a player's opening repertoire against database.

        Args:
            games: List of games
            username: Player's username

        Returns:
            Opening analysis and recommendations
        """
        opening_performance = defaultdict(lambda: {
            "games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "positions": []
        })

        # Analyze each game's opening
        for game in games[:100]:  # Limit to recent 100 games
            # Get opening moves (first 10 moves)
            pgn = game.get("pgn", "")
            moves = self._extract_opening_moves(pgn)

            if not moves:
                continue

            # Determine player color
            white_player = game.get("white", {}).get("username", "").lower()
            black_player = game.get("black", {}).get("username", "").lower()

            if white_player == username.lower():
                color = "white"
                result = game.get("white", {}).get("result", "")
            elif black_player == username.lower():
                color = "black"
                result = game.get("black", {}).get("result", "")
            else:
                continue

            # Get opening name from ECO or moves
            eco = game.get("eco", "")
            opening_name = self._get_opening_name_from_moves(moves, eco)

            # Update statistics
            opening_key = f"{opening_name}_{color}"
            opening_performance[opening_key]["games"] += 1
            opening_performance[opening_key]["positions"].append(moves)

            if "win" in result:
                opening_performance[opening_key]["wins"] += 1
            elif result in ["resigned", "timeout", "checkmated", "abandoned"]:
                opening_performance[opening_key]["losses"] += 1
            else:
                opening_performance[opening_key]["draws"] += 1

        # Compare with database statistics
        recommendations = []
        opening_analysis = []

        for opening_key, stats in opening_performance.items():
            opening_name = opening_key.rsplit("_", 1)[0]
            color = opening_key.rsplit("_", 1)[1]

            # Calculate player's performance
            total_games = stats["games"]
            if total_games > 0:
                win_rate = stats["wins"] / total_games * 100
                loss_rate = stats["losses"] / total_games * 100

                # Get database stats for comparison
                if stats["positions"]:
                    db_stats = self.get_opening_stats(stats["positions"][0], 1500)
                    if db_stats:
                        expected_win_rate = db_stats["statistics"].get(
                            "white_win_rate" if color == "white" else "black_win_rate", 50)

                        performance_diff = win_rate - expected_win_rate

                        analysis_entry = {
                            "opening": opening_name,
                            "color": color,
                            "games": total_games,
                            "player_win_rate": round(win_rate, 1),
                            "expected_win_rate": round(expected_win_rate, 1),
                            "performance_diff": round(performance_diff, 1),
                            "recommendation": self._get_opening_recommendation(
                                win_rate, expected_win_rate, total_games, loss_rate
                            )
                        }
                        opening_analysis.append(analysis_entry)

                        # Generate recommendations
                        if performance_diff < -15 and total_games >= 5:
                            recommendations.append({
                                "priority": "high",
                                "opening": opening_name,
                                "issue": f"Underperforming by {abs(performance_diff):.1f}%",
                                "suggestion": f"Study main lines or consider switching from {opening_name}"
                            })
                        elif performance_diff > 15 and total_games >= 5:
                            recommendations.append({
                                "priority": "low",
                                "opening": opening_name,
                                "issue": f"Performing well (+{performance_diff:.1f}%)",
                                "suggestion": f"Continue playing {opening_name}, explore more variations"
                            })

        # Sort recommendations by priority
        recommendations.sort(key=lambda x: (x["priority"] == "low", -abs(opening_analysis[0]["performance_diff"])))

        return {
            "opening_analysis": opening_analysis,
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "repertoire_summary": self._summarize_repertoire(opening_performance)
        }

    def _extract_opening_moves(self, pgn: str) -> str:
        """Extract opening moves from PGN."""
        try:
            import chess.pgn
            from io import StringIO

            game = chess.pgn.read_game(StringIO(pgn))
            if not game:
                return ""

            board = game.board()
            moves = []

            # Get first 10 moves in UCI format
            for i, move in enumerate(game.mainline_moves()):
                if i >= 20:  # 10 moves for both sides
                    break
                moves.append(move.uci())

            return " ".join(moves)

        except Exception as e:
            print(f"Error extracting moves: {e}")
            return ""

    def _get_opening_name_from_moves(self, moves: str, eco: str = "") -> str:
        """Get opening name from moves or ECO code."""
        # ECO to opening name mapping (partial)
        eco_names = {
            "A00": "Uncommon Opening",
            "A04": "Réti Opening",
            "A05": "Réti Opening",
            "A06": "Réti Opening",
            "A07": "King's Indian Attack",
            "A10": "English Opening",
            "A20": "English Opening",
            "B00": "King's Pawn",
            "B01": "Scandinavian Defense",
            "B10": "Caro-Kann Defense",
            "B12": "Caro-Kann Defense",
            "B20": "Sicilian Defense",
            "B30": "Sicilian Defense",
            "B40": "Sicilian Defense",
            "B50": "Sicilian Defense",
            "C00": "French Defense",
            "C10": "French Defense",
            "C20": "King's Pawn Game",
            "C40": "King's Knight Opening",
            "C41": "Philidor Defense",
            "C42": "Russian Game",
            "C44": "Scotch Game",
            "C45": "Scotch Game",
            "C50": "Italian Game",
            "C55": "Two Knights Defense",
            "C60": "Ruy Lopez",
            "C65": "Ruy Lopez",
            "C70": "Ruy Lopez",
            "D00": "Queen's Pawn Game",
            "D04": "Queen's Pawn Game",
            "D06": "Queen's Gambit",
            "D10": "Slav Defense",
            "D20": "Queen's Gambit Accepted",
            "D30": "Queen's Gambit Declined",
            "D40": "Queen's Gambit Declined",
            "E00": "Queen's Pawn Game",
            "E10": "Queen's Pawn Game",
            "E20": "Nimzo-Indian Defense",
            "E30": "Nimzo-Indian Defense",
            "E40": "Nimzo-Indian Defense",
            "E60": "King's Indian Defense",
            "E70": "King's Indian Defense",
            "E90": "King's Indian Defense",
        }

        if eco and eco in eco_names:
            return eco_names[eco]

        # Default to ECO code if no name found
        return eco if eco else "Unknown Opening"

    def _get_opening_recommendation(self, player_win_rate: float, expected_win_rate: float,
                                   games: int, loss_rate: float) -> str:
        """Generate recommendation for an opening."""
        diff = player_win_rate - expected_win_rate

        if games < 3:
            return "Need more games for accurate assessment"
        elif diff < -20:
            return "Consider switching - significantly underperforming"
        elif diff < -10:
            return "Study main lines and typical plans"
        elif diff < 0:
            return "Minor underperformance - review critical positions"
        elif diff < 10:
            return "Performing as expected - maintain current approach"
        elif diff < 20:
            return "Good performance - explore more complex variations"
        else:
            return "Excellent performance - this is a strength"

    def _summarize_repertoire(self, opening_performance: Dict) -> Dict:
        """Summarize a player's opening repertoire."""
        white_openings = []
        black_openings = []

        for opening_key, stats in opening_performance.items():
            opening_name = opening_key.rsplit("_", 1)[0]
            color = opening_key.rsplit("_", 1)[1]

            if stats["games"] >= 3:  # Only include openings with 3+ games
                entry = {
                    "opening": opening_name,
                    "games": stats["games"],
                    "win_rate": round(stats["wins"] / stats["games"] * 100, 1) if stats["games"] > 0 else 0
                }

                if color == "white":
                    white_openings.append(entry)
                else:
                    black_openings.append(entry)

        # Sort by frequency
        white_openings.sort(key=lambda x: x["games"], reverse=True)
        black_openings.sort(key=lambda x: x["games"], reverse=True)

        return {
            "white_repertoire": white_openings[:5],
            "black_repertoire": black_openings[:5],
            "repertoire_diversity": len(opening_performance),
            "most_played_white": white_openings[0] if white_openings else None,
            "most_played_black": black_openings[0] if black_openings else None
        }

    def suggest_new_openings(self, current_rating: int, color: str,
                            avoid_openings: List[str] = None) -> List[Dict]:
        """
        Suggest new openings to try based on rating and preferences.

        Args:
            current_rating: Player's current rating
            color: "white" or "black"
            avoid_openings: List of openings to avoid

        Returns:
            List of opening suggestions
        """
        avoid_openings = avoid_openings or []
        suggestions = []

        # Popular openings by rating range
        if current_rating < 1000:
            if color == "white":
                candidate_openings = [
                    ("e2e4 e7e5 g1f3", "Italian Game", "Solid and straightforward"),
                    ("e2e4 e7e5 b1c3", "Vienna Game", "Aggressive and tactical"),
                    ("d2d4 d7d5", "Queen's Gambit", "Strategic and solid")
                ]
            else:
                candidate_openings = [
                    ("e2e4 e7e6", "French Defense", "Solid and strategic"),
                    ("e2e4 c7c6", "Caro-Kann Defense", "Very solid"),
                    ("e2e4 e7e5", "Open Games", "Classical and principled")
                ]
        elif current_rating < 1500:
            if color == "white":
                candidate_openings = [
                    ("e2e4 e7e5 g1f3 b8c6 f1b5", "Ruy Lopez", "Rich strategic play"),
                    ("d2d4 d7d5 c2c4", "Queen's Gambit", "Control the center"),
                    ("g1f3", "Réti Opening", "Flexible and modern")
                ]
            else:
                candidate_openings = [
                    ("e2e4 c7c5", "Sicilian Defense", "Counterattacking chances"),
                    ("d2d4 g8f6", "Indian Defenses", "Flexible and dynamic"),
                    ("e2e4 e7e5 g1f3 b8c6", "Italian/Spanish", "Classical defense")
                ]
        else:
            if color == "white":
                candidate_openings = [
                    ("c2c4", "English Opening", "Positional and flexible"),
                    ("d2d4 g8f6 c2c4 g7g6", "King's Indian", "Complex strategic battles"),
                    ("e2e4 e7e5 g1f3 b8c6 f1c4", "Italian Game", "Modern treatment")
                ]
            else:
                candidate_openings = [
                    ("e2e4 c7c5 g1f3 d7d6", "Sicilian Najdorf", "Sharp and complex"),
                    ("d2d4 g8f6 c2c4 e7e6", "Nimzo-Indian", "Positional and solid"),
                    ("e2e4 c7c5 g1f3 e7e6", "Sicilian Taimanov", "Flexible pawn structure")
                ]

        # Get statistics and filter out avoided openings
        for moves, name, description in candidate_openings:
            if name not in avoid_openings:
                stats = self.get_opening_stats(moves, min(2000, ((current_rating // 200) * 200) + 200))
                if stats and stats["statistics"]["total_games"] > 1000:
                    suggestions.append({
                        "name": name,
                        "description": description,
                        "moves": moves,
                        "popularity": stats["statistics"]["total_games"],
                        "win_rate": stats["statistics"][f"{color}_win_rate"],
                        "top_continuation": stats["top_moves"][0]["move"] if stats["top_moves"] else "Various"
                    })

        # Sort by suitability (balance of win rate and popularity)
        suggestions.sort(key=lambda x: x["win_rate"] * 0.7 + min(100, x["popularity"] / 1000) * 0.3,
                        reverse=True)

        return suggestions[:3]


def main():
    """Test the opening database."""
    # Get token from environment
    token = os.environ.get("LICHESS_TOKEN")

    db = OpeningDatabase(token)

    # Test getting stats for Italian Game
    stats = db.get_opening_stats("e2e4 e7e5 g1f3 b8c6 f1c4", 1500)
    if stats:
        print(f"Italian Game statistics at 1500 level:")
        print(f"  Total games: {stats['statistics']['total_games']}")
        print(f"  White wins: {stats['statistics']['white_win_rate']}%")
        print(f"  Top move: {stats['top_moves'][0]['move'] if stats['top_moves'] else 'N/A'}")

    # Test opening suggestions
    suggestions = db.suggest_new_openings(1200, "white")
    print("\nSuggested openings for 1200 rated player (white):")
    for s in suggestions:
        print(f"  - {s['name']}: {s['description']} (win rate: {s['win_rate']}%)")


if __name__ == "__main__":
    main()