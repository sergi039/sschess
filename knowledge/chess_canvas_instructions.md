# Chess Interactive Canvas Instructions

## IMPORTANT: How to Create Chess Board in Interactive Canvas

When user requests chess analysis with Interactive Canvas, follow these EXACT instructions:

### Required CDN Libraries
Always include these in your HTML:

```html
<!-- Chess.js for game logic -->
<script src="https://cdn.jsdelivr.net/npm/chess.js@0.13.4/chess.min.js"></script>

<!-- Chessboard.js for visualization -->
<link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>

<!-- jQuery (required for chessboard.js) -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
```

### Alternative: Lichess PGN Viewer (Recommended)
For full PGN support with analysis:

```html
<link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">
<script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
```

### Chess Piece Images
Use one of these piece sets:

**Option 1: Chessboard.js pieces**
```javascript
var config = {
  pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png'
}
```

**Option 2: Lichess pieces**
```javascript
var config = {
  pieceTheme: 'https://lichess1.org/assets/piece/cburnett/{piece}.svg'
}
```

### Complete Working Example for Interactive Canvas

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chess Analysis</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chess.js@0.13.4/chess.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #2b2b2b;
            color: white;
        }
        #board {
            width: 500px;
            margin: 0 auto;
        }
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        button {
            margin: 5px;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
        .info {
            text-align: center;
            margin: 20px;
        }
    </style>
</head>
<body>
    <div class="info">
        <h2>Chess Game Analysis</h2>
        <p id="status"></p>
    </div>

    <div id="board"></div>

    <div class="controls">
        <button onclick="game.reset(); board.start()">Reset</button>
        <button onclick="board.flip()">Flip Board</button>
        <button onclick="moveBackward()">← Previous</button>
        <button onclick="moveForward()">Next →</button>
    </div>

    <script>
        var board = null;
        var game = new Chess();
        var moveHistory = [];
        var currentMove = 0;

        // Configure board with proper piece images
        var config = {
            draggable: true,
            position: 'start',
            pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png',
            onDrop: handleMove
        };

        board = Chessboard('board', config);

        function handleMove(source, target) {
            var move = game.move({
                from: source,
                to: target,
                promotion: 'q'
            });

            if (move === null) return 'snapback';

            moveHistory.push(move);
            currentMove = moveHistory.length;
            updateStatus();
        }

        function moveForward() {
            // Implementation for forward navigation
        }

        function moveBackward() {
            // Implementation for backward navigation
        }

        function updateStatus() {
            $('#status').html('Move ' + currentMove + ' | ' + (game.turn() === 'w' ? 'White' : 'Black') + ' to move');
        }

        updateStatus();
    </script>
</body>
</html>
```

### For Lichess PGN Viewer

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">
    <script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
</head>
<body>
    <div id="board"></div>
    <script>
        const pgn = `[Event "Live Chess"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6`;

        LichessPgnViewer(document.getElementById('board'), {
            pgn: pgn,
            orientation: 'white',
            showMoves: 'right',
            showClocks: true,
            drawArrows: true,
            viewOnly: false,
            coordinates: true
        });
    </script>
</body>
</html>
```

## Key Requirements for Chess Board in Interactive Canvas

1. **ALWAYS include jQuery** - Required for chessboard.js
2. **ALWAYS specify pieceTheme** - Without it, pieces won't display
3. **Use HTTPS CDN links** - HTTP links may be blocked
4. **Test piece loading** - Verify images are accessible
5. **Include both CSS and JS** - Both are required for proper display

## Troubleshooting

If pieces don't display:
- Check browser console for 404 errors
- Verify CDN links are accessible
- Use alternative piece set URLs
- Ensure jQuery loads before chessboard.js

## Chess Data Format

When receiving chess data from knowledge base:
```json
{
  "pgn": "[Full PGN string]",
  "fen": "starting position FEN",
  "moves": ["e4", "e5", "Nf3"],
  "analysis": {
    "accuracy": 85.5,
    "blunders": 1
  }
}
```

Use this data to populate the board and display analysis.