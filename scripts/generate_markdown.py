#!/usr/bin/env python3
"""
Generate Markdown files for knowledge base from analysis results.

This script converts the JSON analysis into readable Markdown files
that can be consumed by TypingMind or other knowledge base systems.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class MarkdownGenerator:
    """Generates Markdown documentation from chess analysis."""

    def __init__(self, analysis_file: str = "data/analysis_results.json",
                 games_file: str = "data/games_cache.json",
                 output_dir: str = "knowledge"):
        """
        Initialize generator.

        Args:
            analysis_file: Path to analysis results JSON
            games_file: Path to games cache JSON
            output_dir: Directory to save Markdown files
        """
        self.analysis_file = Path(analysis_file)
        self.games_file = Path(games_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.analysis = {}
        self.games_data = {}
        self.load_data()

    def load_data(self):
        """Load analysis and games data."""
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r') as f:
                self.analysis = json.load(f)
        else:
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_file}")

        if self.games_file.exists():
            with open(self.games_file, 'r') as f:
                self.games_data = json.load(f)

    def generate_summary(self):
        """Generate summary.md with overall statistics."""
        username = self.analysis.get("username", "Unknown")
        total_games = self.analysis.get("total_games", 0)
        analysis_date = self.analysis.get("analysis_date", "")

        # Format analysis date
        if analysis_date:
            dt = datetime.fromisoformat(analysis_date)
            formatted_date = dt.strftime("%B %d, %Y at %H:%M")
        else:
            formatted_date = "Unknown"

        content = f"""# Chess Performance Summary for {username}

*Last updated: {formatted_date}*

## Overview

Total games analyzed: **{total_games}**

## Current Ratings

| Time Control | Rating |
|--------------|--------|
"""
        # Add ratings
        ratings = self.analysis.get("rating_progress", {}).get("current_ratings", {})
        for tc, rating in sorted(ratings.items()):
            tc_display = tc.replace("_", " ").title()
            content += f"| {tc_display} | **{rating}** |\n"

        # Performance by time control
        content += "\n## Performance by Time Control\n\n"
        time_controls = self.analysis.get("time_controls", {})

        for tc, stats in sorted(time_controls.items(),
                                key=lambda x: x[1].get("total", 0),
                                reverse=True):
            if stats["total"] > 0:
                tc_display = tc.replace("_", " ").title()
                win_rate = stats.get("win_rate", 0)
                content += f"### {tc_display}\n"
                content += f"- Games: {stats['total']}\n"
                content += f"- Win rate: {win_rate}%\n"
                content += f"- Record: {stats['wins']}W / {stats['losses']}L / {stats['draws']}D\n\n"

        # Overall statistics
        if self.games_data:
            games = self.games_data.get("games", [])
            if games:
                # Recent form (last 20 games)
                recent_games = sorted(games, key=lambda g: g.get("end_time", 0), reverse=True)[:20]
                recent_wins = sum(1 for g in recent_games if self._get_result(g) == "win")
                recent_form = f"{recent_wins}/20"

                content += f"""## Recent Performance

Last 20 games: **{recent_form}** wins ({recent_wins*5}% win rate)

## Time Management

"""
                time_usage = self.analysis.get("time_usage", {})
                timeouts = time_usage.get("timeouts", 0)
                if total_games > 0:
                    timeout_rate = (timeouts / total_games) * 100
                    content += f"- Games lost on time: {timeouts} ({timeout_rate:.1f}%)\n"
                else:
                    content += "- No time management data available\n"

                # Ending types
                endings = time_usage.get("ending_types", {})
                if endings:
                    content += "\n### Most Common Game Endings\n\n"
                    for ending, count in list(endings.items())[:5]:
                        ending_display = ending.replace("_", " ").title()
                        content += f"- {ending_display}: {count} games\n"

        # Save file
        output_file = self.output_dir / "summary.md"
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Generated: {output_file}")

    def generate_openings(self):
        """Generate openings.md with opening repertoire analysis."""
        content = f"""# Opening Repertoire Analysis

*Based on {self.analysis.get('total_games', 0)} games*

## Playing as White

"""
        # White openings
        white_openings = self.analysis.get("openings", {}).get("white", {})
        sorted_white = sorted(white_openings.items(),
                             key=lambda x: x[1].get("total", 0),
                             reverse=True)

        if sorted_white:
            content += "| Opening | Games | Win Rate | Performance |\n"
            content += "|---------|-------|----------|-------------|\n"

            for opening, stats in sorted_white[:10]:  # Top 10
                total = stats["total"]
                win_rate = stats.get("win_rate", 0)
                wins = stats["wins"]
                losses = stats["losses"]
                draws = stats["draws"]

                # Performance indicator
                if win_rate >= 60:
                    indicator = "🟢"
                elif win_rate >= 45:
                    indicator = "🟡"
                else:
                    indicator = "🔴"

                content += f"| {opening} | {total} | {win_rate}% | {indicator} {wins}W/{losses}L/{draws}D |\n"

        # Black openings
        content += "\n## Playing as Black\n\n"
        black_openings = self.analysis.get("openings", {}).get("black", {})
        sorted_black = sorted(black_openings.items(),
                             key=lambda x: x[1].get("total", 0),
                             reverse=True)

        if sorted_black:
            content += "| Opening | Games | Win Rate | Performance |\n"
            content += "|---------|-------|----------|-------------|\n"

            for opening, stats in sorted_black[:10]:  # Top 10
                total = stats["total"]
                win_rate = stats.get("win_rate", 0)
                wins = stats["wins"]
                losses = stats["losses"]
                draws = stats["draws"]

                # Performance indicator
                if win_rate >= 55:  # Slightly lower threshold for black
                    indicator = "🟢"
                elif win_rate >= 40:
                    indicator = "🟡"
                else:
                    indicator = "🔴"

                content += f"| {opening} | {total} | {win_rate}% | {indicator} {wins}W/{losses}L/{draws}D |\n"

        # Recommendations
        content += "\n## Recommendations\n\n"

        # Find best performing openings
        best_white = None
        best_black = None

        for opening, stats in sorted_white:
            if stats["total"] >= 10 and stats.get("win_rate", 0) > 50:
                best_white = (opening, stats)
                break

        for opening, stats in sorted_black:
            if stats["total"] >= 10 and stats.get("win_rate", 0) > 45:
                best_black = (opening, stats)
                break

        if best_white:
            content += f"### Continue with White:\n"
            content += f"- **{best_white[0]}** - {best_white[1]['win_rate']}% win rate in {best_white[1]['total']} games\n\n"

        if best_black:
            content += f"### Continue with Black:\n"
            content += f"- **{best_black[0]}** - {best_black[1]['win_rate']}% win rate in {best_black[1]['total']} games\n\n"

        # Save file
        output_file = self.output_dir / "openings.md"
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Generated: {output_file}")

    def generate_weaknesses(self):
        """Generate weaknesses.md with areas for improvement."""
        content = """# Areas for Improvement

*Identified weaknesses and recommendations based on game analysis*

## Critical Issues

"""
        weaknesses = self.analysis.get("weaknesses", {}).get("identified_weaknesses", [])

        if weaknesses:
            for i, weakness in enumerate(weaknesses, 1):
                if weakness["type"] == "opening":
                    content += f"""### {i}. Problematic Opening ({weakness['color'].title()})

**Opening:** {weakness['opening']}
- Games played: {weakness['games']}
- Loss rate: {weakness['loss_rate']}%

**Recommendation:** Consider studying this opening more deeply or switching to an alternative.

"""
                elif weakness["type"] == "time_management":
                    content += f"""### {i}. Time Management Issues

{weakness['description']}

**Recommendations:**
- Practice faster decision-making in familiar positions
- Learn pattern recognition to save time
- Consider playing longer time controls until improvement

"""
        else:
            content += "*No significant weaknesses identified. Keep up the good work!*\n\n"

        # Add general improvement areas based on statistics
        content += """## General Improvement Areas

### 1. Opening Preparation
- Study main lines of your most played openings
- Prepare responses to common opponent moves
- Focus on understanding plans rather than memorizing moves

### 2. Endgame Technique
- Practice basic endgames (K+P, K+R, K+Q)
- Study theoretical positions
- Focus on calculation accuracy in simplified positions

### 3. Time Management
- Set time targets for opening phase (e.g., 10% of total time)
- Practice rapid decision-making in familiar positions
- Avoid time trouble by maintaining steady pace

### 4. Tactical Awareness
- Daily tactical puzzles (15-30 minutes)
- Focus on pattern recognition
- Practice calculation of forcing variations
"""

        # Add specific openings to study
        problem_openings = []
        for color in ["white", "black"]:
            openings = self.analysis.get("openings", {}).get(color, {})
            for opening, stats in openings.items():
                if stats["total"] >= 5 and stats.get("loss_rate", 0) > 40:
                    problem_openings.append((opening, color, stats))

        if problem_openings:
            content += "\n## Specific Openings to Study\n\n"
            for opening, color, stats in problem_openings[:5]:
                content += f"- **{opening}** (as {color}): "
                content += f"{stats['loss_rate']}% loss rate in {stats['total']} games\n"

        # Save file
        output_file = self.output_dir / "weaknesses.md"
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Generated: {output_file}")

    def generate_recent_games(self):
        """Generate recent_games.md with latest games for reference."""
        content = """# Recent Games

*Last 20 games with key details*

| Date | Opponent | Rating | Color | Result | Opening | Time Control | Link |
|------|----------|--------|-------|--------|---------|--------------|------|
"""
        if self.games_data:
            games = self.games_data.get("games", [])
            username = self.games_data.get("username", "").lower()

            # Sort by end time and get last 20
            recent = sorted(games, key=lambda g: g.get("end_time", 0), reverse=True)[:20]

            for game in recent:
                # Extract data
                end_time = game.get("end_time", 0)
                date = datetime.fromtimestamp(end_time).strftime("%Y-%m-%d") if end_time else "N/A"

                # Determine color and opponent
                white_player = game.get("white", {}).get("username", "").lower()
                black_player = game.get("black", {}).get("username", "").lower()

                if white_player == username:
                    color = "⚪"
                    opponent = game.get("black", {}).get("username", "Unknown")
                    opponent_rating = game.get("black", {}).get("rating", "?")
                    result = self._format_result(game.get("white", {}).get("result", ""))
                else:
                    color = "⚫"
                    opponent = game.get("white", {}).get("username", "Unknown")
                    opponent_rating = game.get("white", {}).get("rating", "?")
                    result = self._format_result(game.get("black", {}).get("result", ""))

                # Get opening (simplified)
                opening = self._get_opening_simple(game)
                time_control = game.get("time_class", "?").replace("_", " ").title()
                url = game.get("url", "#")

                # Format result with emoji
                if "win" in result.lower():
                    result_display = "✅ Won"
                elif "loss" in result.lower() or "resign" in result.lower() or "timeout" in result.lower():
                    result_display = "❌ Lost"
                else:
                    result_display = "➖ Draw"

                content += f"| {date} | {opponent} | {opponent_rating} | {color} | {result_display} | {opening} | {time_control} | [View]({url}) |\n"

        # Add analysis section
        content += """

## Quick Stats from Recent Games

"""
        if recent:
            recent_wins = sum(1 for g in recent if "win" in self._get_result_str(g))
            recent_losses = sum(1 for g in recent if "loss" in self._get_result_str(g))
            recent_draws = len(recent) - recent_wins - recent_losses

            content += f"- **Record:** {recent_wins}W / {recent_losses}L / {recent_draws}D\n"
            content += f"- **Win rate:** {(recent_wins/len(recent)*100):.1f}%\n"

            # Most faced opponent
            opponents = {}
            for g in recent:
                white = g.get("white", {}).get("username", "")
                black = g.get("black", {}).get("username", "")
                opp = white if black.lower() == username else black
                if opp:
                    opponents[opp] = opponents.get(opp, 0) + 1

            if opponents:
                most_played = max(opponents.items(), key=lambda x: x[1])
                content += f"- **Most faced:** {most_played[0]} ({most_played[1]} games)\n"

        # Save file
        output_file = self.output_dir / "recent_games.md"
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Generated: {output_file}")

    def _get_result(self, game: Dict) -> str:
        """Helper to get game result."""
        username = self.games_data.get("username", "").lower()
        white_player = game.get("white", {}).get("username", "").lower()
        black_player = game.get("black", {}).get("username", "").lower()

        if white_player == username:
            result = game.get("white", {}).get("result", "")
        elif black_player == username:
            result = game.get("black", {}).get("result", "")
        else:
            return "unknown"

        if "win" in result:
            return "win"
        elif result in ["resigned", "timeout", "checkmated", "abandoned"]:
            return "loss"
        else:
            return "draw"

    def _get_result_str(self, game: Dict) -> str:
        """Helper to get result string."""
        result = self._get_result(game)
        return result

    def _format_result(self, result: str) -> str:
        """Format result string for display."""
        if "win" in result:
            return "Won"
        elif "agreed" in result:
            return "Draw"
        elif "repetition" in result:
            return "Draw (repetition)"
        elif "insufficient" in result:
            return "Draw (insufficient)"
        elif "timeout" in result:
            return "Lost (timeout)"
        elif "resigned" in result:
            return "Lost (resigned)"
        elif "checkmated" in result:
            return "Lost (checkmate)"
        elif "abandoned" in result:
            return "Lost (abandoned)"
        else:
            return result

    def _get_opening_simple(self, game: Dict) -> str:
        """Extract opening name from game (simplified)."""
        pgn = game.get("pgn", "")
        if "[Opening " in pgn:
            start = pgn.index("[Opening ") + 9
            end = pgn.index("]", start)
            opening = pgn[start:end].strip('"')
            # Shorten if too long
            if len(opening) > 20:
                opening = opening[:17] + "..."
            return opening
        return "Unknown"

    def generate_all(self):
        """Generate all Markdown files."""
        print("\nGenerating Markdown files...")
        self.generate_summary()
        self.generate_openings()
        self.generate_weaknesses()
        self.generate_recent_games()
        print(f"\nAll files generated in: {self.output_dir}/")


def main():
    """Main function to run the generator."""
    # Check if analysis file exists
    analysis_file = Path("data/analysis_results.json")
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found. Run analyze.py first.")
        return

    # Generate Markdown files
    generator = MarkdownGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()