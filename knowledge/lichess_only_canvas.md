# Lichess-Only Interactive Canvas Instructions

## IMPORTANT: Use ONLY Lichess Components (NO Chess.com!)

When creating Interactive Canvas for chess analysis, use ONLY these components:

### Required: Lichess PGN Viewer

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lichess Chess Analysis</title>
    <link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #262421;
            color: #bababa;
            font-family: 'Noto Sans', Arial, sans-serif;
        }
        #board {
            max-width: 800px;
            margin: 0 auto;
        }
        .info {
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin: 10px 0;
        }
        .stat {
            background: #2b2b2b;
            padding: 10px 15px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="info">
        <h2>📊 Анализ партии Lichess</h2>
        <div class="stats">
            <div class="stat">⚪ White: {white_player}</div>
            <div class="stat">⚫ Black: {black_player}</div>
            <div class="stat">📅 Date: {date}</div>
        </div>
    </div>

    <div id="board"></div>

    <script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
    <script>
        // PGN from your game
        const pgn = `{pgn_data}`;

        // Initialize Lichess PGN Viewer
        LichessPgnViewer(document.getElementById('board'), {
            pgn: pgn,
            orientation: 'white',
            showMoves: 'right',
            showClocks: true,
            drawArrows: true,
            viewOnly: false,
            coordinates: true,
            addTo: 'body',
            menu: {
                getPgn: true,
                practise: false,
                analysisBoard: false
            }
        });
    </script>
</body>
</html>
```

## Alternative: ChessboardJS (if Lichess viewer fails)

If lichess-pgn-viewer doesn't work, use this alternative:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chess Analysis</title>
    <!-- jQuery MUST be first -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

    <!-- Then ChessboardJS CSS -->
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">

    <!-- Then ChessboardJS -->
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>

    <!-- Then Chess.js -->
    <script src="https://cdn.jsdelivr.net/npm/chess.js@0.13.4/chess.min.js"></script>

    <style>
        body {
            background: #262421;
            color: white;
            font-family: Arial;
            padding: 20px;
        }
        #myBoard {
            width: 500px;
            margin: 20px auto;
        }
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        button {
            margin: 5px;
            padding: 10px 20px;
            background: #629924;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #7bc143;
        }
        .info {
            text-align: center;
            margin: 20px;
            background: #1e1e1e;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="info">
        <h2>Chess Analysis - Lichess Style</h2>
        <p id="status">Ready</p>
    </div>

    <div id="myBoard"></div>

    <div class="controls">
        <button onclick="board.start()">Start Position</button>
        <button onclick="board.flip()">Flip Board</button>
        <button onclick="previousMove()">◀ Previous</button>
        <button onclick="nextMove()">Next ▶</button>
    </div>

    <script>
        var board = null;
        var game = new Chess();
        var moveList = [];
        var currentMove = 0;

        // CRITICAL: Specify piece images!
        var config = {
            draggable: true,
            position: 'start',
            onDragStart: onDragStart,
            onDrop: onDrop,
            onSnapEnd: onSnapEnd,
            pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png'
        };

        board = Chessboard('myBoard', config);

        function onDragStart(source, piece, position, orientation) {
            if (game.game_over()) return false;
            if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
                (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
                return false;
            }
        }

        function onDrop(source, target) {
            var move = game.move({
                from: source,
                to: target,
                promotion: 'q'
            });

            if (move === null) return 'snapback';

            moveList.push(move);
            currentMove = moveList.length;
            updateStatus();
        }

        function onSnapEnd() {
            board.position(game.fen());
        }

        function updateStatus() {
            var status = '';
            var moveColor = 'White';
            if (game.turn() === 'b') moveColor = 'Black';

            if (game.in_checkmate()) {
                status = 'Game over, ' + moveColor + ' is in checkmate.';
            } else if (game.in_draw()) {
                status = 'Game over, drawn position';
            } else {
                status = moveColor + ' to move';
                if (game.in_check()) status += ', ' + moveColor + ' is in check';
            }

            document.getElementById('status').innerHTML = status;
        }

        function previousMove() {
            if (currentMove > 0) {
                currentMove--;
                // Reset game and replay moves
                game.reset();
                for (var i = 0; i < currentMove; i++) {
                    game.move(moveList[i]);
                }
                board.position(game.fen());
                updateStatus();
            }
        }

        function nextMove() {
            if (currentMove < moveList.length) {
                game.move(moveList[currentMove]);
                currentMove++;
                board.position(game.fen());
                updateStatus();
            }
        }

        updateStatus();
    </script>
</body>
</html>
```

## Key Points for Success:

1. **NO Chess.com components** - Use only Lichess or ChessboardJS
2. **jQuery MUST load first** if using ChessboardJS
3. **pieceTheme is REQUIRED** - Without it, no pieces show
4. **Use HTTPS CDN links only**
5. **Test in browser console** for errors

## For PGN with moves:

```javascript
// Load PGN into chess.js
const pgn = "[Event 'Game']\\n1. e4 e5 2. Nf3 Nc6";
game.load_pgn(pgn);

// Get all moves
const moves = game.history();

// Display on board
board.position(game.fen());
```

## Troubleshooting Checklist:

✅ jQuery loaded before ChessboardJS?
✅ pieceTheme URL specified?
✅ All CDN links use HTTPS?
✅ Console shows no 404 errors?
✅ Board element ID matches JavaScript?

## DO NOT USE:
- ❌ Chess.com API
- ❌ Chess.com embed
- ❌ Chess.com analysis board
- ❌ Any Chess.com components

## USE ONLY:
- ✅ Lichess PGN Viewer
- ✅ ChessboardJS + Chess.js
- ✅ Local analysis with Stockfish data