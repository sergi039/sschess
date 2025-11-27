#!/usr/bin/env python3
"""
Analyze chess games to find patterns, openings, and weaknesses.

This script analyzes the fetched games to extract insights like:
- Most played openings and success rates
- Performance by time control
- Common time trouble situations
- Strengths and weaknesses
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class ChessAnalyzer:
    """Analyzes chess games for patterns and insights."""

    # Common opening patterns (simplified)
    OPENING_PATTERNS = {
        "e4": "King's Pawn",
        "d4": "Queen's Pawn",
        "Nf3": "Reti Opening",
        "c4": "English Opening",
        "e4 e5": "King's Pawn Game",
        "e4 c5": "Sicilian Defense",
        "e4 e6": "French Defense",
        "e4 c6": "Caro-Kann Defense",
        "d4 Nf6": "Indian Defense",
        "d4 d5": "Closed Game",
        "e4 e5 Nf3": "King's Knight Opening",
        "e4 e5 Nf3 Nc6": "Four Knights",
        "e4 e5 Nf3 Nc6 Bb5": "Ruy Lopez",
        "e4 e5 Nf3 Nc6 Bc4": "Italian Game",
        "d4 Nf6 c4": "Indian Systems",
        "d4 d5 c4": "Queen's Gambit",
        "d4 Nf6 c4 g6": "King's Indian",
        "d4 Nf6 c4 e6": "Nimzo/Queen's Indian",
    }

    def __init__(self, cache_file: str = "data/games_cache.json"):
        """
        Initialize analyzer.

        Args:
            cache_file: Path to games cache file
        """
        self.cache_file = Path(cache_file)
        self.games = []
        self.username = ""
        self.load_games()

    def load_games(self):
        """Load games from cache file."""
        if not self.cache_file.exists():
            raise FileNotFoundError(f"Cache file not found: {self.cache_file}")

        with open(self.cache_file, 'r') as f:
            data = json.load(f)

        self.username = data.get("username", "").lower()
        self.games = data.get("games", [])
        print(f"Loaded {len(self.games)} games for {self.username}")

    def get_player_color(self, game: Dict) -> str:
        """Determine if player was white or black in a game."""
        white_player = game.get("white", {}).get("username", "").lower()
        black_player = game.get("black", {}).get("username", "").lower()

        if white_player == self.username:
            return "white"
        elif black_player == self.username:
            return "black"
        return "unknown"

    def get_game_result(self, game: Dict) -> str:
        """Get game result from player's perspective."""
        color = self.get_player_color(game)
        if color == "unknown":
            return "unknown"

        player_data = game.get(color, {})
        opponent_data = game.get("white" if color == "black" else "black", {})

        player_result = player_data.get("result", "")
        opponent_result = opponent_data.get("result", "")

        if "win" in player_result:
            return "win"
        elif "win" in opponent_result:
            return "loss"
        elif "agreed" in player_result or "repetition" in player_result or "insufficient" in player_result:
            return "draw"
        elif player_result in ["resigned", "timeout", "checkmated", "abandoned"]:
            return "loss"
        elif opponent_result in ["resigned", "timeout", "checkmated", "abandoned"]:
            return "win"
        else:
            return "draw"

    def get_opening(self, game: Dict) -> str:
        """Extract opening from PGN or moves."""
        pgn = game.get("pgn", "")
        if not pgn:
            return "Unknown"

        # Try to get ECO code from PGN headers
        if "[ECO " in pgn:
            eco_start = pgn.index("[ECO ") + 5
            eco_end = pgn.index("]", eco_start)
            eco_code = pgn[eco_start:eco_end].strip('"')
            if eco_code:
                return f"ECO {eco_code}"

        # Try to get opening name from PGN headers
        if "[Opening " in pgn:
            opening_start = pgn.index("[Opening ") + 9
            opening_end = pgn.index("]", opening_start)
            opening_name = pgn[opening_start:opening_end].strip('"')
            if opening_name:
                return opening_name

        # Extract first moves and match patterns
        moves_start = pgn.rfind("]") + 1
        moves_text = pgn[moves_start:].strip()

        # Parse moves (simplified)
        moves = []
        for token in moves_text.split():
            if not token[0].isdigit() and not token.startswith("{") and token != "*":
                moves.append(token.split("+")[0].split("#")[0])  # Remove check/mate symbols
                if len(moves) >= 6:  # Look at first 3 full moves
                    break

        # Match against known patterns (longest first)
        moves_str = " ".join(moves)
        for pattern_length in [5, 4, 3, 2, 1]:
            test_pattern = " ".join(moves[:pattern_length])
            if test_pattern in self.OPENING_PATTERNS:
                return self.OPENING_PATTERNS[test_pattern]

        # Default based on first move
        if moves:
            return f"1. {moves[0]}"
        return "Unknown"

    def analyze_openings(self) -> Dict:
        """Analyze opening repertoire and success rates."""
        openings_white = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0})
        openings_black = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0})

        for game in self.games:
            color = self.get_player_color(game)
            result = self.get_game_result(game)
            opening = self.get_opening(game)

            if color == "white":
                openings_white[opening]["total"] += 1
                if result == "win":
                    openings_white[opening]["wins"] += 1
                elif result == "loss":
                    openings_white[opening]["losses"] += 1
                elif result == "draw":
                    openings_white[opening]["draws"] += 1
            elif color == "black":
                openings_black[opening]["total"] += 1
                if result == "win":
                    openings_black[opening]["wins"] += 1
                elif result == "loss":
                    openings_black[opening]["losses"] += 1
                elif result == "draw":
                    openings_black[opening]["draws"] += 1

        # Calculate win rates
        for openings in [openings_white, openings_black]:
            for opening_data in openings.values():
                total = opening_data["total"]
                if total > 0:
                    opening_data["win_rate"] = round(opening_data["wins"] / total * 100, 1)
                    opening_data["loss_rate"] = round(opening_data["losses"] / total * 100, 1)

        return {
            "white": dict(openings_white),
            "black": dict(openings_black)
        }

    def analyze_time_controls(self) -> Dict:
        """Analyze performance by time control."""
        time_controls = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0})

        for game in self.games:
            tc = game.get("time_class", "unknown")
            result = self.get_game_result(game)

            time_controls[tc]["total"] += 1
            if result == "win":
                time_controls[tc]["wins"] += 1
            elif result == "loss":
                time_controls[tc]["losses"] += 1
            elif result == "draw":
                time_controls[tc]["draws"] += 1

        # Calculate win rates
        for tc_data in time_controls.values():
            total = tc_data["total"]
            if total > 0:
                tc_data["win_rate"] = round(tc_data["wins"] / total * 100, 1)

        return dict(time_controls)

    def analyze_time_usage(self) -> Dict:
        """Analyze time management patterns."""
        time_pressure_games = []
        endings = Counter()

        for game in self.games:
            color = self.get_player_color(game)
            if color == "unknown":
                continue

            # Check for time pressure (simplified - would need move times for accurate analysis)
            player_data = game.get(color, {})
            result_reason = player_data.get("result", "")

            if "timeout" in result_reason:
                time_pressure_games.append({
                    "url": game.get("url", ""),
                    "result": "lost on time",
                    "time_control": game.get("time_class", "unknown")
                })

            # Track ending types
            if result_reason:
                endings[result_reason] += 1

        return {
            "timeouts": len(time_pressure_games),
            "timeout_games": time_pressure_games[:5],  # Show only first 5
            "ending_types": dict(endings.most_common(10))
        }

    def analyze_rating_progress(self) -> Dict:
        """Analyze rating changes over time."""
        rating_history = []

        for game in sorted(self.games, key=lambda g: g.get("end_time", 0)):
            color = self.get_player_color(game)
            if color == "unknown":
                continue

            player_data = game.get(color, {})
            rating = player_data.get("rating")
            if rating:
                timestamp = game.get("end_time", 0)
                date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else "unknown"
                rating_history.append({
                    "date": date,
                    "rating": rating,
                    "time_control": game.get("time_class", "unknown")
                })

        # Group by time control
        by_time_control = defaultdict(list)
        for entry in rating_history:
            tc = entry["time_control"]
            by_time_control[tc].append({
                "date": entry["date"],
                "rating": entry["rating"]
            })

        # Get current ratings (last games)
        current_ratings = {}
        for tc, history in by_time_control.items():
            if history:
                current_ratings[tc] = history[-1]["rating"]

        return {
            "current_ratings": current_ratings,
            "total_games_tracked": len(rating_history)
        }

    def find_weaknesses(self) -> Dict:
        """Identify potential weaknesses and areas for improvement."""
        weaknesses = []

        # Analyze openings
        openings = self.analyze_openings()

        # Find problematic openings as white
        for opening, stats in openings["white"].items():
            if stats["total"] >= 5:  # Only consider if played enough times
                if stats.get("loss_rate", 0) > 40:
                    weaknesses.append({
                        "type": "opening",
                        "color": "white",
                        "opening": opening,
                        "games": stats["total"],
                        "loss_rate": stats.get("loss_rate", 0)
                    })

        # Find problematic openings as black
        for opening, stats in openings["black"].items():
            if stats["total"] >= 5:
                if stats.get("loss_rate", 0) > 45:  # Slightly higher threshold for black
                    weaknesses.append({
                        "type": "opening",
                        "color": "black",
                        "opening": opening,
                        "games": stats["total"],
                        "loss_rate": stats.get("loss_rate", 0)
                    })

        # Check time management
        time_analysis = self.analyze_time_usage()
        timeout_rate = (time_analysis["timeouts"] / len(self.games) * 100) if self.games else 0
        if timeout_rate > 5:
            weaknesses.append({
                "type": "time_management",
                "description": f"Lost {time_analysis['timeouts']} games on time ({timeout_rate:.1f}% of all games)"
            })

        # Sort by severity
        weaknesses.sort(key=lambda x: x.get("loss_rate", x.get("games", 0)), reverse=True)

        return {
            "identified_weaknesses": weaknesses[:5],  # Top 5 weaknesses
            "total_issues": len(weaknesses)
        }

    def generate_analysis(self) -> Dict:
        """Generate complete analysis."""
        print("Analyzing games...")

        analysis = {
            "username": self.username,
            "total_games": len(self.games),
            "analysis_date": datetime.now().isoformat(),
            "openings": self.analyze_openings(),
            "time_controls": self.analyze_time_controls(),
            "time_usage": self.analyze_time_usage(),
            "rating_progress": self.analyze_rating_progress(),
            "weaknesses": self.find_weaknesses()
        }

        # Save analysis
        output_file = Path("data/analysis_results.json")
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Analysis saved to: {output_file}")
        return analysis


def main():
    """Main function to run the analyzer."""
    # Check if cache file exists
    cache_file = "data/games_cache.json"
    if not Path(cache_file).exists():
        print(f"Error: {cache_file} not found. Run fetch_games.py first.")
        return

    # Run analysis
    analyzer = ChessAnalyzer(cache_file)
    analysis = analyzer.generate_analysis()

    # Print summary
    print("\n" + "=" * 50)
    print("ANALYSIS SUMMARY")
    print("=" * 50)

    print(f"\nPlayer: {analysis['username']}")
    print(f"Total games analyzed: {analysis['total_games']}")

    # Current ratings
    print("\nCurrent Ratings:")
    for tc, rating in analysis["rating_progress"]["current_ratings"].items():
        print(f"  {tc}: {rating}")

    # Top openings
    print("\nMost Played Openings (White):")
    white_openings = sorted(
        analysis["openings"]["white"].items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )[:3]
    for opening, stats in white_openings:
        print(f"  {opening}: {stats['total']} games, {stats.get('win_rate', 0)}% win rate")

    print("\nMost Played Openings (Black):")
    black_openings = sorted(
        analysis["openings"]["black"].items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )[:3]
    for opening, stats in black_openings:
        print(f"  {opening}: {stats['total']} games, {stats.get('win_rate', 0)}% win rate")

    # Weaknesses
    if analysis["weaknesses"]["identified_weaknesses"]:
        print("\nIdentified Weaknesses:")
        for weakness in analysis["weaknesses"]["identified_weaknesses"][:3]:
            if weakness["type"] == "opening":
                print(f"  - {weakness['color'].title()}: {weakness['opening']} "
                      f"({weakness['loss_rate']}% loss rate in {weakness['games']} games)")
            else:
                print(f"  - {weakness.get('description', weakness['type'])}")


if __name__ == "__main__":
    main()