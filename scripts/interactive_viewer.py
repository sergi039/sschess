#!/usr/bin/env python3
"""
Interactive chess game viewer with Lichess-like interface.

This module generates HTML with embedded lichess-pgn-viewer for
interactive game analysis directly in TypingMind chat.
"""

import json
import chess
import chess.pgn
from io import StringIO
from typing import Dict, List, Optional
from pathlib import Path


class InteractiveChessViewer:
    """Generate interactive HTML chess viewer with Lichess interface."""

    def __init__(self):
        """Initialize the viewer."""
        self.template = self._load_template()

    def _load_template(self) -> str:
        """Load the HTML template for the viewer."""
        # Note: Using double braces {{ }} to escape CSS braces for format()
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Analysis</title>
    <style>
        body {{
            font-family: 'Noto Sans', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #262421;
            color: #bababa;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #1e1e1e;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}

        .header {{
            background: linear-gradient(135deg, #7c4dff 0%, #536dfe 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .players {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .player {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 600;
        }}

        .rating {{
            opacity: 0.9;
            font-size: 16px;
        }}

        .result {{
            font-size: 24px;
            font-weight: bold;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
        }}

        .analysis-stats {{
            background: #2b2b2b;
            padding: 15px 20px;
            display: flex;
            gap: 30px;
            border-bottom: 1px solid #404040;
        }}

        .stat {{
            display: flex;
            flex-direction: column;
        }}

        .stat-label {{
            font-size: 12px;
            color: #888;
            margin-bottom: 4px;
        }}

        .stat-value {{
            font-size: 20px;
            font-weight: bold;
        }}

        .stat-value.good {{ color: #4caf50; }}
        .stat-value.medium {{ color: #ff9800; }}
        .stat-value.bad {{ color: #f44336; }}

        #pgn-viewer {{
            background: #262421;
            min-height: 600px;
        }}

        /* Override lichess-pgn-viewer styles for dark theme */
        .lpv {{
            background: #262421 !important;
        }}

        .lpv__moves {{
            background: #1e1e1e !important;
            color: #bababa !important;
        }}

        .lpv__moves move {{
            color: #bababa !important;
        }}

        .lpv__moves move:hover {{
            background: #404040 !important;
        }}

        .lpv__moves move.active {{
            background: #536dfe !important;
            color: white !important;
        }}

        .lpv__board {{
            margin: 20px;
        }}

        /* Evaluation bar styling */
        .eval-bar {{
            position: absolute;
            left: -30px;
            top: 0;
            bottom: 0;
            width: 20px;
            background: linear-gradient(to bottom,
                white 0%,
                white var(--eval-percent),
                #404040 var(--eval-percent),
                #404040 100%
            );
            border: 1px solid #404040;
            border-radius: 3px;
        }}

        .legend {{
            padding: 20px;
            background: #2b2b2b;
            border-top: 1px solid #404040;
        }}

        .legend-title {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #bababa;
        }}

        .legend-items {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }}

        .legend-symbol {{
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
        }}

        .brilliant {{ background: #1bada0; color: white; }}
        .best {{ background: #4caf50; color: white; }}
        .excellent {{ background: #66bb6a; color: white; }}
        .good {{ background: #81c784; color: white; }}
        .inaccuracy {{ background: #ff9800; color: white; }}
        .mistake {{ background: #f44336; color: white; }}
        .blunder {{ background: #b71c1c; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="players">
                <div class="player">
                    <span>⚪</span>
                    <span>{white_player}</span>
                    <span class="rating">({white_rating})</span>
                </div>
                <div class="player">
                    <span>⚫</span>
                    <span>{black_player}</span>
                    <span class="rating">({black_rating})</span>
                </div>
            </div>
            <div class="result">{result}</div>
        </div>

        <div class="analysis-stats">
            <div class="stat">
                <div class="stat-label">Accuracy</div>
                <div class="stat-value {accuracy_class}">{accuracy}%</div>
            </div>
            <div class="stat">
                <div class="stat-label">Blunders</div>
                <div class="stat-value {blunder_class}">{blunders}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Mistakes</div>
                <div class="stat-value {mistake_class}">{mistakes}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Inaccuracies</div>
                <div class="stat-value">{inaccuracies}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Average Centipawn Loss</div>
                <div class="stat-value">{acpl}</div>
            </div>
        </div>

        <div id="pgn-viewer"></div>

        <div class="legend">
            <div class="legend-title">Move Classifications</div>
            <div class="legend-items">
                <div class="legend-item">
                    <span class="legend-symbol brilliant">!!</span>
                    <span>Brilliant move</span>
                </div>
                <div class="legend-item">
                    <span class="legend-symbol best">!</span>
                    <span>Best move</span>
                </div>
                <div class="legend-item">
                    <span class="legend-symbol good">Good</span>
                    <span>Good move</span>
                </div>
                <div class="legend-item">
                    <span class="legend-symbol inaccuracy">?!</span>
                    <span>Inaccuracy</span>
                </div>
                <div class="legend-item">
                    <span class="legend-symbol mistake">?</span>
                    <span>Mistake</span>
                </div>
                <div class="legend-item">
                    <span class="legend-symbol blunder">??</span>
                    <span>Blunder</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Lichess PGN Viewer -->
    <link rel="stylesheet" href="https://lichess1.org/assets/css/lpv.min.css">
    <script src="https://lichess1.org/assets/js/lpv.min.js"></script>

    <script>
        // Initialize lichess-pgn-viewer
        const pgn = `{annotated_pgn}`;

        LichessPgnViewer(document.getElementById('pgn-viewer'), {{{{
            pgn: pgn,
            orientation: 'white',
            coordinates: true,
            showPlayers: false,  // We show custom header
            showMoves: 'right',
            showClocks: true,
            drawArrows: true,
            viewOnly: false,
            menu: {{{{
                getPgn: true,
                practise: false,
                analysisBoard: true
            }}}},
            lichess: 'https://lichess.org/',
            classes: 'lpv--dark'
        }}}});
    </script>
</body>
</html>
        """

    def create_annotated_pgn(self, game: Dict, analysis: Dict) -> str:
        """
        Create PGN with analysis annotations.

        Args:
            game: Game data from cache
            analysis: Stockfish analysis results

        Returns:
            Annotated PGN string
        """
        # Parse original PGN
        original_pgn = game.get("pgn", "")
        pgn_game = chess.pgn.read_game(StringIO(original_pgn))

        if not pgn_game:
            return original_pgn

        # Create new game with annotations
        annotated_game = chess.pgn.Game()

        # Copy headers
        for key, value in pgn_game.headers.items():
            annotated_game.headers[key] = value

        # Add custom headers
        if analysis.get("accuracy"):
            annotated_game.headers["WhiteAccuracy"] = str(analysis["accuracy"])
            annotated_game.headers["BlackAccuracy"] = str(analysis["accuracy"])

        # Process moves with analysis
        board = annotated_game.board()
        node = annotated_game

        moves = list(pgn_game.mainline_moves())
        analysis_data = analysis.get("analysis", [])

        for i, move in enumerate(moves):
            # Add the move
            node = node.add_variation(move)

            # Add analysis annotations if available
            if i < len(analysis_data):
                move_analysis = analysis_data[i]
                classification = move_analysis.get("classification", "")
                eval_loss = move_analysis.get("eval_loss", 0)
                best_move = move_analysis.get("best_move", "")

                # Add NAG (Numeric Annotation Glyph) based on classification
                if classification == "brilliant":
                    node.nags.add(chess.pgn.NAG_BRILLIANT_MOVE)  # !!
                elif classification == "best":
                    node.nags.add(chess.pgn.NAG_GOOD_MOVE)  # !
                elif classification == "inaccuracy":
                    node.nags.add(chess.pgn.NAG_DUBIOUS_MOVE)  # ?!
                elif classification == "mistake":
                    node.nags.add(chess.pgn.NAG_MISTAKE)  # ?
                elif classification == "blunder":
                    node.nags.add(chess.pgn.NAG_BLUNDER)  # ??

                # Add comment with evaluation
                if eval_loss and abs(eval_loss) > 50:
                    eval_loss_pawns = eval_loss / 100
                    if best_move and best_move != str(move):
                        node.comment = f"Lost {abs(eval_loss_pawns):.1f} pawns. Better was {best_move}"
                    else:
                        node.comment = f"Evaluation: {eval_loss_pawns:+.1f}"

                # Add variation with best move if significantly different
                if best_move and best_move != str(move) and abs(eval_loss) > 100:
                    try:
                        # Go back to parent to add variation
                        parent = node.parent
                        best_move_obj = board.parse_san(best_move)
                        var_node = parent.add_variation(best_move_obj)
                        var_node.comment = "Best move"
                    except:
                        pass  # Skip if move parsing fails

            board.push(move)

        # Generate PGN string
        exporter = StringIO()
        exporter.write(str(annotated_game))
        return exporter.getvalue()

    def generate_viewer_html(self, game: Dict, analysis: Dict) -> str:
        """
        Generate complete HTML with interactive viewer.

        Args:
            game: Game data from cache
            analysis: Analysis results

        Returns:
            Complete HTML string
        """
        # Extract game info
        white = game.get("white", {})
        black = game.get("black", {})

        white_player = white.get("username", "White")
        black_player = black.get("username", "Black")
        white_rating = white.get("rating", "?")
        black_rating = black.get("rating", "?")

        # Determine result
        white_result = white.get("result", "")
        if white_result == "win":
            result = "1-0"
        elif white_result == "lose":
            result = "0-1"
        elif white_result in ["draw", "agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]:
            result = "½-½"
        else:
            result = "*"

        # Get analysis stats
        accuracy = analysis.get("accuracy", 0)
        blunders = analysis.get("blunders", 0)
        mistakes = analysis.get("mistakes", 0)
        inaccuracies = analysis.get("inaccuracies", 0)

        # Calculate average centipawn loss
        acpl = 0
        if analysis.get("analysis"):
            total_loss = sum(abs(m.get("eval_loss", 0)) for m in analysis["analysis"])
            move_count = len(analysis["analysis"])
            if move_count > 0:
                acpl = round(total_loss / move_count)

        # Determine CSS classes for coloring
        accuracy_class = "good" if accuracy >= 90 else "medium" if accuracy >= 75 else "bad"
        blunder_class = "bad" if blunders > 2 else "medium" if blunders > 0 else "good"
        mistake_class = "bad" if mistakes > 3 else "medium" if mistakes > 1 else "good"

        # Create annotated PGN
        annotated_pgn = self.create_annotated_pgn(game, analysis)

        # Escape for JavaScript
        annotated_pgn = annotated_pgn.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

        # Fill template
        html = self.template.format(
            white_player=white_player,
            black_player=black_player,
            white_rating=white_rating,
            black_rating=black_rating,
            result=result,
            accuracy=round(accuracy, 1),
            accuracy_class=accuracy_class,
            blunders=blunders,
            blunder_class=blunder_class,
            mistakes=mistakes,
            mistake_class=mistake_class,
            inaccuracies=inaccuracies,
            acpl=acpl,
            annotated_pgn=annotated_pgn
        )

        return html

    def save_viewer_html(self, html: str, filename: str = "chess_viewer.html") -> str:
        """
        Save HTML to file for testing.

        Args:
            html: HTML content
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = Path("data") / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)


def main():
    """Test the interactive viewer."""
    import sys
    import json

    # Load test data
    cache_file = Path("data/games_cache.json")
    analysis_cache = Path("data/detailed_analysis_cache.json")

    if not cache_file.exists():
        print("No games cache found")
        return

    with open(cache_file, 'r') as f:
        games_data = json.load(f)
        games = games_data.get("games", [])

    if not games:
        print("No games in cache")
        return

    # Get latest game
    game = games[0]
    print(f"Creating viewer for game: {game.get('url', 'Unknown')}")

    # Load or create analysis
    analysis = {}
    if analysis_cache.exists():
        with open(analysis_cache, 'r') as f:
            cached = json.load(f)
            game_id = game.get("url", "")
            if game_id in cached:
                analysis = cached[game_id]

    if not analysis:
        # Create mock analysis for testing
        analysis = {
            "accuracy": 85.5,
            "blunders": 1,
            "mistakes": 2,
            "inaccuracies": 3,
            "analysis": []
        }

    # Generate HTML
    viewer = InteractiveChessViewer()
    html = viewer.generate_viewer_html(game, analysis)

    # Save to file
    output_file = viewer.save_viewer_html(html)
    print(f"Interactive viewer saved to: {output_file}")
    print("Open this file in a browser to test the viewer")


if __name__ == "__main__":
    main()