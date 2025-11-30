#!/usr/bin/env python3
"""
TypingMind-specific chess viewer that generates markdown with embedded HTML.
This module creates output specifically formatted for TypingMind's rendering.
"""

import json
import base64
from pathlib import Path
from typing import Dict, Optional


class TypingMindChessViewer:
    """Generate TypingMind-compatible chess analysis output."""

    def generate_markdown_with_board(self, game: Dict, analysis: Dict) -> str:
        """
        Generate markdown output with embedded chess board for TypingMind.

        Args:
            game: Game data from cache
            analysis: Analysis results

        Returns:
            Markdown string with embedded HTML that TypingMind can render
        """
        # Extract game info
        white = game.get("white", {})
        black = game.get("black", {})

        white_player = white.get("username", "White")
        black_player = black.get("username", "Black")
        white_rating = white.get("rating", "?")
        black_rating = black.get("rating", "?")

        # Get result
        white_result = white.get("result", "")
        if white_result == "win":
            result = "1-0"
            result_text = f"{white_player} won"
        elif white_result == "lose":
            result = "0-1"
            result_text = f"{black_player} won"
        else:
            result = "½-½"
            result_text = "Draw"

        # Get analysis stats
        accuracy = analysis.get("accuracy", 0)
        blunders = analysis.get("blunders", 0)
        mistakes = analysis.get("mistakes", 0)
        inaccuracies = analysis.get("inaccuracies", 0)

        # Get PGN
        pgn = game.get("pgn", "")

        # Create the HTML board using lichess-pgn-viewer
        html_board = f"""
<div id="board-{game.get('url', '').split('/')[-1]}" style="width: 100%; max-width: 800px; margin: 20px auto;"></div>
<link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">
<script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const pgn = `{pgn}`;
    LichessPgnViewer(document.getElementById('board-{game.get('url', '').split('/')[-1]}'), {{
        pgn: pgn,
        orientation: 'white',
        showMoves: 'right',
        showClocks: false,
        drawArrows: true,
        viewOnly: false,
        coordinates: true,
        menu: {{
            getPgn: false,
            practise: false,
            analysisBoard: false
        }}
    }});
}});
</script>
"""

        # Generate markdown with embedded HTML
        markdown_output = f"""# 🎯 Chess Game Analysis

## 📋 Game Information

**{white_player} ({white_rating}) vs {black_player} ({black_rating})**
**Result:** {result} - {result_text}

## 📊 Computer Analysis

| Metric | Value | Rating |
|--------|-------|--------|
| **Accuracy** | {accuracy:.1f}% | {'🟢 Excellent' if accuracy >= 90 else '🟡 Good' if accuracy >= 75 else '🔴 Need improvement'} |
| **Blunders** | {blunders} | {'🔴' if blunders > 2 else '🟡' if blunders > 0 else '🟢'} |
| **Mistakes** | {mistakes} | {'🔴' if mistakes > 3 else '🟡' if mistakes > 1 else '🟢'} |
| **Inaccuracies** | {inaccuracies} | {'🟡' if inaccuracies > 5 else '🟢'} |

## 🎮 Interactive Board

{html_board}

## 📝 Key Moments

"""

        # Add critical moves if available
        if analysis.get("analysis"):
            critical_moves = [m for m in analysis["analysis"]
                            if m.get("classification") in ["blunder", "mistake"]][:5]

            if critical_moves:
                markdown_output += "### Biggest Mistakes:\n\n"
                for move_data in critical_moves:
                    move_num = move_data.get("move_number", "?")
                    move = move_data.get("move", "")
                    best = move_data.get("best_move", "")
                    loss = abs(move_data.get("eval_loss", 0)) / 100

                    symbol = "??" if move_data["classification"] == "blunder" else "?"

                    markdown_output += f"**Move {move_num}. {move} {symbol}**\n"
                    markdown_output += f"- Lost {loss:.1f} pawns of advantage\n"
                    if best and best != move:
                        markdown_output += f"- Better was: {best}\n"
                    markdown_output += "\n"

        # Add game link
        markdown_output += f"""
## 🔗 Links

- [View original game on Chess.com]({game.get('url', '#')})
- Game analyzed with Stockfish engine

---
*Use arrow keys or click moves to navigate through the game*
"""

        return markdown_output

    def generate_simple_board(self, game: Dict, analysis: Dict) -> str:
        """
        Generate a simpler ASCII-style board if HTML doesn't work.

        This is a fallback option for maximum compatibility.
        """
        pgn = game.get("pgn", "")
        moves = pgn.split()

        # Create move list
        move_pairs = []
        for i in range(0, len(moves), 3):  # Skip move numbers
            if i+1 < len(moves):
                white_move = moves[i+1] if i+1 < len(moves) else ""
                black_move = moves[i+2] if i+2 < len(moves) else ""
                if white_move and not white_move[0].isdigit():
                    move_pairs.append((white_move, black_move))

        output = f"""# 🎯 Chess Game Analysis

## 📊 Analysis Summary

- **Accuracy:** {analysis.get('accuracy', 0):.1f}%
- **Blunders:** {analysis.get('blunders', 0)}
- **Mistakes:** {analysis.get('mistakes', 0)}
- **Inaccuracies:** {analysis.get('inaccuracies', 0)}

## 📝 Move List

```
"""
        for i, (white, black) in enumerate(move_pairs, 1):
            output += f"{i:3}. {white:8} {black:8}\n"
            if i % 10 == 0:
                output += "\n"

        output += "```\n"

        return output


def create_typingmind_output(game: Dict, analysis: Dict) -> str:
    """
    Main function to create TypingMind-compatible output.

    Args:
        game: Game data
        analysis: Analysis results

    Returns:
        Markdown string optimized for TypingMind rendering
    """
    viewer = TypingMindChessViewer()
    return viewer.generate_markdown_with_board(game, analysis)


if __name__ == "__main__":
    # Test with sample data
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from analyze_game_on_demand import OnDemandAnalyzer

    analyzer = OnDemandAnalyzer()
    game = analyzer.find_game("2025-11-29")

    if game:
        # Get or create analysis
        game_id = game.get("url", "")
        if game_id in analyzer.cached_analysis:
            analysis = analyzer.cached_analysis[game_id]
        else:
            analysis = {
                "accuracy": 85.5,
                "blunders": 1,
                "mistakes": 2,
                "inaccuracies": 3,
                "analysis": []
            }

        output = create_typingmind_output(game, analysis)
        print(output)

        # Save to file for testing
        with open("data/typingmind_output.md", "w") as f:
            f.write(output)
        print("\nOutput saved to data/typingmind_output.md")
    else:
        print("No game found for testing")