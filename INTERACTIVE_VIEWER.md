# 🎯 Interactive Chess Viewer Documentation

## Overview

The Interactive Chess Viewer provides a **Lichess-like interface** for analyzing chess games directly within TypingMind chat. It uses the official `lichess-pgn-viewer` library to create an interactive chess board with full analysis features.

## Features

### 🎮 Interactive Board
- **Drag & drop pieces** - Move pieces to explore variations
- **Arrow keys navigation** - Use ← → to navigate through moves
- **Click on moves** - Jump to any position by clicking moves in the list
- **Flip board** - Press 'f' to flip the board perspective
- **Coordinates** - Board coordinates for easy reference

### 📊 Analysis Display
- **Accuracy percentage** - Overall game accuracy score
- **Move classifications** - Visual indicators for blunders (??), mistakes (?), inaccuracies (?!), and brilliant moves (!!)
- **Centipawn loss** - Average centipawn loss per move
- **Best move suggestions** - Shows better alternatives for mistakes
- **Evaluation comments** - Stockfish evaluation in move comments

### 🎨 Visual Design
- **Dark theme** - Lichess-style dark interface
- **Color-coded stats** - Green for good, orange for medium, red for poor performance
- **Player information** - Names, ratings, and game result
- **Move list** - Scrollable move list with highlighting
- **Legend** - Clear explanation of move symbols

## Usage in TypingMind

### Basic Command
```
Analyze my chess game from [date/opponent]
```

### Examples
- "Analyze my game from November 29"
- "Analyze my game against player123"
- "Show interactive analysis of my last game"

### What Happens
1. System finds the game in your database
2. Runs Stockfish computer analysis (if not cached)
3. Generates interactive HTML viewer
4. Embeds viewer directly in TypingMind chat
5. You can interact with the board right in the chat!

## Technical Implementation

### Components
1. **`interactive_viewer.py`** - Generates the HTML viewer
2. **`analyze_game_on_demand.py`** - Integrates viewer with analysis
3. **lichess-pgn-viewer** - Official Lichess board library
4. **Stockfish** - Chess engine for analysis

### HTML Structure
```html
<div class="container">
  <div class="header">Players & Result</div>
  <div class="analysis-stats">Accuracy, Blunders, etc.</div>
  <div id="pgn-viewer">Interactive Board</div>
  <div class="legend">Move Classifications</div>
</div>
```

### PGN Annotations
The system adds:
- NAGs (Numeric Annotation Glyphs) for move quality
- Comments with evaluation and best moves
- Variations showing better alternatives

## Comparison with Text Report

| Feature | Interactive Viewer | Text Report |
|---------|-------------------|-------------|
| Board visualization | ✅ Interactive | ❌ No board |
| Move navigation | ✅ Click/arrows | ❌ Static list |
| Variations | ✅ Explorable | ✅ Listed |
| Analysis depth | ✅ Full details | ✅ Summary |
| User experience | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## Benefits

1. **No External Tools** - Everything works within TypingMind
2. **Instant Analysis** - Cached results load immediately
3. **Professional Interface** - Same quality as Lichess.org
4. **Educational** - Learn from mistakes with visual feedback
5. **Shareable** - Download HTML file to share analysis

## Requirements

- Stockfish installed locally (for new analysis)
- Modern browser with JavaScript enabled
- TypingMind with HTML rendering support

## Future Enhancements

- [ ] Real-time evaluation graph
- [ ] Opening book integration
- [ ] Multiple game comparison
- [ ] Puzzle generation from critical positions
- [ ] Export to Lichess Study

## Troubleshooting

### Board not showing?
- Check JavaScript is enabled in TypingMind
- Try refreshing the chat

### Analysis not running?
- Ensure Stockfish is installed: `brew install stockfish`
- Check games are cached: `data/games_cache.json`

### Slow performance?
- First analysis takes ~30 seconds
- Subsequent views use cache (instant)

---

*Interactive Chess Viewer - Bringing Lichess-quality analysis to TypingMind*