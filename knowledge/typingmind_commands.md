# TypingMind Chess Commands

## Available Commands for Chess Analysis

### 1. Analyze Specific Game
```
Analyze my chess game from [date/opponent/description]
```

**Examples:**
- "Analyze my game from November 29"
- "Analyze my game against player123"
- "Analyze my last game"
- "Analyze the game where I played the Sicilian"

**What it does:**
- Finds the game in your database
- Runs Stockfish computer analysis
- Shows accuracy, mistakes, blunders
- Provides Lichess-style report

### 2. Show Recent Performance
```
Show my recent chess performance
```

**What it shows:**
- Last 20 games results
- Win/loss/draw statistics
- Rating changes
- Common openings played

### 3. Opening Analysis
```
How do I play against [opening name]?
```

**Examples:**
- "How do I play against the Sicilian?"
- "What are my stats in the Italian Game?"
- "Show my performance with e4 openings"

### 4. Find Patterns
```
What are my common mistakes?
```

**What it analyzes:**
- Recurring blunders
- Time management issues
- Opening weaknesses
- Endgame problems

### 5. Compare with Database
```
Compare my [opening] performance with masters
```

**What it shows:**
- Your win rate vs expected
- Common mistakes in the opening
- Recommended improvements

## How to Use in TypingMind

1. **Basic Stats** - Always available from cached data
2. **Deep Analysis** - Requires game-specific request
3. **Computer Analysis** - On-demand with Stockfish

## Integration Setup

For TypingMind to use these commands:

1. The knowledge base must be synced (✓ Already done)
2. Python scripts must be accessible
3. Stockfish engine should be installed (for full analysis)

## API Endpoints

The system provides these analysis endpoints:

- `/analyze_game` - Analyze specific game
- `/recent_games` - Show recent performance
- `/opening_stats` - Opening repertoire analysis
- `/weakness_report` - Identify patterns

## Examples of Analysis Output

### Accuracy Report
```
📊 Game Analysis
Accuracy: 87.3%
Blunders: 1
Mistakes: 2
Inaccuracies: 4

Critical Moments:
Move 15. Nxe5?? - Blunder, loses piece
Better was: 15. Bd3
```

### Opening Performance
```
Italian Game (as White)
Games: 23
Win rate: 65.2%
Expected: 54.1%
Performance: +11.1% ✅
```

## Tips for Best Results

1. **Be specific** in your requests (dates, opponents, openings)
2. **Recent games** have more detailed analysis
3. **Computer analysis** takes ~30 seconds per game
4. **Cached results** load instantly

---

*This document helps TypingMind understand available chess analysis commands*