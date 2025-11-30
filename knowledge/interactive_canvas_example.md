# Interactive Canvas Example for Chess Analysis

When displaying a game in TypingMind, use this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chess Game Analysis</title>

    <!-- Lichess PGN Viewer -->
    <link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">

    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #262421;
            color: #bababa;
            font-family: 'Noto Sans', Arial, sans-serif;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .info {
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .stat {
            background: #2b2b2b;
            padding: 12px 16px;
            border-radius: 6px;
        }
        .stat-label {
            color: #888;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .stat-value {
            color: #fff;
            font-size: 18px;
            font-weight: 500;
        }
        #board {
            background: white;
            border-radius: 8px;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="info">
            <h2>♟️ Game Analysis</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">White</div>
                    <div class="stat-value">{white_player}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Black</div>
                    <div class="stat-value">{black_player}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Result</div>
                    <div class="stat-value">{result}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Date</div>
                    <div class="stat-value">{date}</div>
                </div>
            </div>
        </div>

        <div id="board"></div>
    </div>

    <script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
    <script>
        // Replace {pgn_data} with actual PGN from games_summary.json
        const pgn = `{pgn_data}`;

        LichessPgnViewer(document.getElementById('board'), {
            pgn: pgn,
            orientation: 'white',
            showMoves: 'right',
            showClocks: true,
            drawArrows: true,
            viewOnly: false,
            coordinates: true,
            addTo: 'body',
            scrollToMove: true,
            showPlayers: true,
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

## How to use this template:

1. Load game from `games_summary.json`
2. Extract the PGN from `game['pgn']`
3. Replace placeholders:
   - `{white_player}` with white player name
   - `{black_player}` with black player name
   - `{result}` with game result
   - `{date}` with game date
   - `{pgn_data}` with the actual PGN string

## Example usage with data:

```javascript
// Load the game data
const gameData = // load from games_summary.json
const game = gameData.games.find(g => /* your search criteria */);

// Extract information
const pgn = game.pgn;
const white = game.white.username || game.white;
const black = game.black.username || game.black;
const result = game.result;
const date = new Date(game.end_time * 1000).toLocaleDateString();

// Use in template
const html = template
    .replace('{white_player}', white)
    .replace('{black_player}', black)
    .replace('{result}', result)
    .replace('{date}', date)
    .replace('{pgn_data}', pgn.replace(/`/g, '\\`'));
```