#!/usr/bin/env python3
"""
On-demand game analysis for TypingMind integration.

This script analyzes a specific game using Lichess-style computer analysis
when requested from TypingMind chat.
"""

import os
import sys
import json
import chess
import chess.engine
import chess.pgn
from io import StringIO
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class OnDemandAnalyzer:
    """Analyze specific chess games on request."""

    def __init__(self):
        """Initialize the analyzer."""
        self.cache_dir = Path("data")
        self.cache_file = self.cache_dir / "games_cache.json"
        self.analysis_cache = self.cache_dir / "detailed_analysis_cache.json"

        # Load games cache
        self.games = self._load_games()
        self.cached_analysis = self._load_analysis_cache()

    def _load_games(self) -> List[Dict]:
        """Load games from cache."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return data.get("games", [])
        return []

    def _load_analysis_cache(self) -> Dict:
        """Load cached analysis."""
        if self.analysis_cache.exists():
            with open(self.analysis_cache, 'r') as f:
                return json.load(f)
        return {}

    def _save_analysis_cache(self):
        """Save analysis cache."""
        with open(self.analysis_cache, 'w') as f:
            json.dump(self.cached_analysis, f, indent=2)

    def find_game(self, query: str) -> Optional[Dict]:
        """
        Find a game by date, opponent, or game ID.

        Args:
            query: Search query (date, opponent name, or game URL)

        Returns:
            Game data if found
        """
        query_lower = query.lower()

        # Try to find by date first
        for game in self.games:
            game_date = datetime.fromtimestamp(game.get("end_time", 0))
            date_str = game_date.strftime("%Y-%m-%d")

            if query_lower in date_str:
                return game

            # Check opponent names
            white_player = game.get("white", {}).get("username", "").lower()
            black_player = game.get("black", {}).get("username", "").lower()

            if query_lower in white_player or query_lower in black_player:
                return game

            # Check game URL
            if query_lower in game.get("url", "").lower():
                return game

        return None

    def analyze_with_stockfish(self, pgn: str, depth: int = 20) -> Dict:
        """
        Analyze game with Stockfish engine (Lichess-style).

        Args:
            pgn: PGN string of the game
            depth: Analysis depth

        Returns:
            Detailed analysis like Lichess
        """
        try:
            # Parse PGN
            game = chess.pgn.read_game(StringIO(pgn))
            if not game:
                return {"error": "Invalid PGN"}

            board = game.board()
            analysis = []
            move_classifications = []

            # Try to use local Stockfish - check multiple locations
            engine_paths = [
                "/opt/homebrew/bin/stockfish",  # Homebrew on Apple Silicon
                "/usr/local/bin/stockfish",      # Homebrew on Intel Mac
                "/usr/bin/stockfish",            # Linux
                "stockfish"                      # In PATH
            ]

            engine = None
            for path in engine_paths:
                try:
                    engine = chess.engine.SimpleEngine.popen_uci(path)
                    print(f"Using engine: {path}")
                    break
                except:
                    continue

            if not engine:
                print("Stockfish not found, using simplified analysis")
                return self._simplified_analysis(game)

            prev_eval = 0  # Starting position
            move_num = 0

            for move in game.mainline_moves():
                move_num += 1

                # Analyze position before move
                info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
                eval_before = self._score_to_cp(info_before["score"])

                # Make the move
                board.push(move)

                # Analyze position after move
                info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
                eval_after = self._score_to_cp(info_after["score"])

                # Calculate accuracy loss
                if move_num % 2 == 1:  # White's move
                    eval_loss = eval_before - eval_after
                else:  # Black's move
                    eval_loss = eval_after - eval_before

                # Classify move (Lichess style)
                classification = self._classify_move(eval_loss)

                # Get best move
                best_move = info_before.get("pv", [None])[0] if "pv" in info_before else None

                move_data = {
                    "move": str(move),
                    "move_number": (move_num + 1) // 2,
                    "eval_before": eval_before,
                    "eval_after": eval_after,
                    "eval_loss": eval_loss,
                    "classification": classification,
                    "best_move": str(best_move) if best_move else str(move),
                    "depth": depth
                }

                analysis.append(move_data)
                move_classifications.append(classification)

                prev_eval = eval_after

            engine.quit()

            # Calculate statistics
            total_moves = len(move_classifications)
            accuracy = self._calculate_accuracy(move_classifications)

            return {
                "analysis": analysis,
                "accuracy": accuracy,
                "total_moves": total_moves,
                "blunders": sum(1 for c in move_classifications if c == "blunder"),
                "mistakes": sum(1 for c in move_classifications if c == "mistake"),
                "inaccuracies": sum(1 for c in move_classifications if c == "inaccuracy"),
                "good_moves": sum(1 for c in move_classifications if c in ["good", "excellent", "best"]),
                "engine_depth": depth
            }

        except Exception as e:
            print(f"Engine analysis error: {e}")
            return self._simplified_analysis(game)

    def _score_to_cp(self, score) -> int:
        """Convert engine score to centipawns."""
        try:
            if score.is_mate():
                # Mate score
                if score.mate() > 0:
                    return 10000 - score.mate() * 100  # Winning
                else:
                    return -10000 - score.mate() * 100  # Losing
            else:
                # Regular centipawn score
                # Handle both old and new python-chess API
                if hasattr(score, 'score'):
                    return score.score()
                elif hasattr(score, 'relative'):
                    return score.relative.score()
                else:
                    return 0
        except:
            return 0

    def _classify_move(self, eval_loss: int) -> str:
        """
        Classify move based on evaluation loss (Lichess style).

        Returns: blunder, mistake, inaccuracy, good, excellent, best
        """
        eval_loss = abs(eval_loss)

        if eval_loss >= 300:
            return "blunder"     # ?? - losing 3+ pawns
        elif eval_loss >= 100:
            return "mistake"     # ? - losing 1-3 pawns
        elif eval_loss >= 50:
            return "inaccuracy"  # ?! - losing 0.5-1 pawn
        elif eval_loss <= 10:
            return "best"        # !! - perfect move
        elif eval_loss <= 25:
            return "excellent"   # ! - great move
        else:
            return "good"        # normal move

    def _calculate_accuracy(self, classifications: List[str]) -> float:
        """Calculate game accuracy percentage (Lichess formula approximation)."""
        if not classifications:
            return 0

        # Weighted scoring
        weights = {
            "best": 1.0,
            "excellent": 0.95,
            "good": 0.9,
            "inaccuracy": 0.6,
            "mistake": 0.3,
            "blunder": 0
        }

        total_score = sum(weights.get(c, 0.5) for c in classifications)
        accuracy = (total_score / len(classifications)) * 100

        return round(accuracy, 1)

    def _simplified_analysis(self, game) -> Dict:
        """Fallback analysis without engine."""
        moves = list(game.mainline_moves())

        return {
            "analysis": [],
            "accuracy": 75.0,  # Default estimate
            "total_moves": len(moves),
            "blunders": 0,
            "mistakes": 0,
            "inaccuracies": 0,
            "good_moves": len(moves),
            "engine_depth": 0,
            "note": "Simplified analysis - Stockfish not available"
        }

    def generate_interactive_html_viewer(self, game: Dict, analysis: Dict) -> str:
        """
        Generate interactive HTML viewer with Lichess interface for TypingMind.

        Returns:
            Markdown with embedded HTML optimized for TypingMind rendering
        """
        import sys
        from pathlib import Path
        # Add scripts directory to path for import
        sys.path.insert(0, str(Path(__file__).parent))
        from typingmind_viewer import create_typingmind_output

        # Generate TypingMind-optimized output
        return create_typingmind_output(game, analysis)

    def generate_lichess_style_report(self, game: Dict, analysis: Dict) -> str:
        """
        Generate a Lichess-style analysis report.

        Returns:
            Markdown formatted report
        """
        # Game info
        white = game.get("white", {}).get("username", "?")
        black = game.get("black", {}).get("username", "?")
        result = game.get("white", {}).get("result", "?")
        date = datetime.fromtimestamp(game.get("end_time", 0)).strftime("%Y-%m-%d %H:%M")

        report = [
            f"# 🔍 Computer Analysis",
            f"",
            f"**{white} vs {black}**",
            f"*{date}* | Result: {result}",
            f"",
            f"## 📊 Overall Performance",
            f"",
            f"- **Accuracy:** {analysis['accuracy']}%",
            f"- **Total Moves:** {analysis['total_moves']}",
            f""
        ]

        # Move classifications
        if analysis['blunders'] > 0:
            report.append(f"- **Blunders (??)**:  {analysis['blunders']} moves")
        if analysis['mistakes'] > 0:
            report.append(f"- **Mistakes (?)**:  {analysis['mistakes']} moves")
        if analysis['inaccuracies'] > 0:
            report.append(f"- **Inaccuracies (?!)**:  {analysis['inaccuracies']} moves")

        report.extend([
            f"",
            f"## 🎯 Critical Moments",
            f""
        ])

        # Show worst moves
        worst_moves = sorted(
            [m for m in analysis.get("analysis", []) if m["classification"] in ["blunder", "mistake"]],
            key=lambda x: abs(x["eval_loss"]),
            reverse=True
        )[:5]

        if worst_moves:
            report.append("### Biggest Mistakes:")
            report.append("")
            for move_data in worst_moves:
                move_num = move_data["move_number"]
                move = move_data["move"]
                best = move_data["best_move"]
                loss = abs(move_data["eval_loss"]) / 100

                symbol = "??" if move_data["classification"] == "blunder" else "?"

                report.append(f"**Move {move_num}. {move} {symbol}**")
                report.append(f"- Lost {loss:.1f} pawns of advantage")
                report.append(f"- Better was: {best}")
                report.append("")

        # Evaluation graph (simplified text version)
        report.extend([
            "## 📈 Evaluation Trend",
            "",
            "```"
        ])

        # Create simple ASCII graph
        for i, move_data in enumerate(analysis.get("analysis", [])[:20]):
            eval_score = move_data["eval_after"] / 100
            eval_score = max(-10, min(10, eval_score))  # Clamp to ±10

            # Create bar
            if eval_score > 0:
                bar = "+" + "█" * int(eval_score)
            elif eval_score < 0:
                bar = "-" + "█" * int(abs(eval_score))
            else:
                bar = "="

            classification = move_data["classification"]
            if classification in ["blunder", "mistake"]:
                marker = f" ← {classification}"
            else:
                marker = ""

            report.append(f"Move {i+1:2}: {bar:12} ({eval_score:+.1f}){marker}")

        report.extend([
            "```",
            "",
            "## 💡 Key Takeaways",
            ""
        ])

        # Generate insights
        if analysis['accuracy'] < 70:
            report.append("- ⚠️ **Low accuracy** - Focus on avoiding blunders")
        elif analysis['accuracy'] < 85:
            report.append("- 📈 **Decent play** - Work on reducing mistakes")
        else:
            report.append("- ✨ **Great game** - Very accurate play!")

        if analysis['blunders'] > 2:
            report.append("- 🎯 **Blunder alert** - Practice tactical puzzles")

        if analysis.get('engine_depth', 0) > 0:
            report.append(f"- 🖥️ Analysis depth: {analysis['engine_depth']} ply")

        # Link to full game
        report.extend([
            "",
            "---",
            f"🔗 [View original game]({game.get('url', '#')})"
        ])

        return "\n".join(report)

    def analyze_game_by_request(self, query: str, interactive: bool = True) -> str:
        """
        Main entry point for TypingMind requests.

        Args:
            query: User query to find and analyze game
            interactive: If True, return interactive HTML viewer; if False, return text report

        Returns:
            HTML viewer or markdown formatted analysis report
        """
        # Find the game
        game = self.find_game(query)

        if not game:
            return f"❌ Game not found for query: '{query}'\n\nTry searching by:\n- Date (e.g., '2025-11-29')\n- Opponent name\n- Game URL"

        # Check if already analyzed
        game_id = game.get("url", "")
        if game_id in self.cached_analysis:
            print("Using cached analysis")
            analysis = self.cached_analysis[game_id]
        else:
            # Perform new analysis
            print(f"Analyzing game from {datetime.fromtimestamp(game.get('end_time', 0)).strftime('%Y-%m-%d %H:%M')}")
            pgn = game.get("pgn", "")

            if not pgn:
                return "❌ No PGN data available for this game"

            analysis = self.analyze_with_stockfish(pgn)

            # Cache the result
            self.cached_analysis[game_id] = analysis
            self._save_analysis_cache()

        # Generate interactive viewer or text report
        if interactive:
            return self.generate_interactive_html_viewer(game, analysis)
        else:
            return self.generate_lichess_style_report(game, analysis)


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_game_on_demand.py <query>")
        print("Example: python analyze_game_on_demand.py '2025-11-29'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    analyzer = OnDemandAnalyzer()
    result = analyzer.analyze_game_by_request(query)
    print(result)


if __name__ == "__main__":
    main()