# 🔍 Lichess Integration Documentation

## Overview

This chess knowledge base now includes comprehensive Lichess integration for advanced game analysis, providing:

- 🎯 **Computer Analysis**: Accuracy metrics, blunder/mistake detection
- ⚔️ **Tactical Patterns**: Recognition of forks, pins, skewers, and more
- 📚 **Opening Database**: Performance comparison with global statistics
- 📖 **Study Generation**: Interactive Lichess studies for training
- 📈 **Improvement Plans**: Personalized recommendations based on weaknesses

## Setup

### 1. Get Your Lichess API Token

1. Go to https://lichess.org/account/oauth/token
2. Create a new personal access token
3. Select the following scopes:
   - `Read preferences` (required)
   - `Create, update, and read studies` (for study generation)
   - `Read game playing` (optional)

### 2. Configure Token

#### For Local Development
Add to `.env` file:
```bash
LICHESS_TOKEN=lip_YourTokenHere
```

#### For GitHub Actions
Add as repository secret:
1. Go to Settings → Secrets → Actions
2. Add new secret: `LICHESS_TOKEN`
3. Paste your token value

## Usage

### Basic Usage (with Lichess analysis)
```bash
python scripts/main.py
```

### Skip Lichess Analysis
```bash
python scripts/main.py --skip-lichess
```

### Full Analysis of Recent Games
```bash
python scripts/main.py --months 3
```

## Features

### 1. Computer Analysis (`lichess_analyzer.py`)

Analyzes games using Lichess's Stockfish engine:
- Game accuracy percentage
- Blunder detection (>300 centipawn loss)
- Mistake detection (>100 centipawn loss)
- Inaccuracy detection (>50 centipawn loss)
- Move-by-move evaluations
- Best move suggestions

**Output**: `knowledge/lichess_accuracy.md`, `knowledge/lichess_mistakes.md`

### 2. Tactical Pattern Detection (`tactical_detector.py`)

Identifies tactical themes in your games:
- **Forks**: Attacking multiple pieces simultaneously
- **Pins**: Absolute and relative pins
- **Skewers**: Forcing valuable pieces to move
- **Discovered Attacks**: Revealing hidden threats
- **Double Attacks**: Attacking two targets
- **Sacrifices**: Material sacrifices for advantage
- **Back Rank Threats**: Exploiting weak back ranks

**Output**: `knowledge/lichess_tactics.md`

### 3. Opening Database Integration (`opening_database.py`)

Compares your openings with Lichess database:
- Win rate comparison with expected rates
- Opening popularity at your rating level
- Performance differential analysis
- Repertoire diversity metrics
- New opening suggestions based on rating

**Output**: `knowledge/lichess_openings.md`

### 4. Lichess Study Generator (`study_generator.py`)

Creates interactive studies on Lichess:
- **Opening Repertoire Study**: Your most played openings with statistics
- **Improvement Study**: Games with most mistakes for learning
- **Tactical Patterns Study**: Positions demonstrating tactical themes

**Output**: `knowledge/lichess_studies.md` (contains study links)

### 5. Personalized Improvement Plan

Generates actionable recommendations:
- Priority areas based on weaknesses
- Weekly training schedule
- Progress tracking metrics
- Specific exercises for improvement

**Output**: `knowledge/lichess_improvement.md`

## Generated Files

After running with Lichess integration, you'll have:

```
knowledge/
├── summary.md              # Basic statistics
├── openings.md             # Opening repertoire
├── weaknesses.md           # Areas for improvement
├── recent_games.md         # Recent game list
├── lichess_accuracy.md     # Computer analysis report
├── lichess_mistakes.md     # Mistake analysis
├── lichess_tactics.md      # Tactical patterns found
├── lichess_openings.md     # Opening recommendations
├── lichess_improvement.md  # Personalized training plan
└── lichess_studies.md      # Links to Lichess studies

data/
├── games_cache.json         # Chess.com games cache
├── analysis_results.json    # Basic analysis results
├── lichess_analysis_cache.json  # Lichess analysis cache
└── opening_database.json    # Opening statistics cache
```

## API Rate Limits

The integration respects Lichess API rate limits:
- Automatic delays between requests
- Caching to avoid repeated analysis
- Limited to 20 games for computer analysis (configurable)

## Advanced Configuration

### Customize Analysis Depth

Edit `lichess_analyzer.py`:
```python
# Analyze more games (default is 20)
games[:50]  # Analyze 50 games instead
```

### Skip Computer Analysis (Faster)

For faster analysis without engine evaluation:
```bash
python scripts/main.py --skip-lichess
```

### Manual Lichess Analysis

Run just the Lichess analysis on existing cache:
```python
from scripts.lichess_analyzer import LichessAnalyzer
analyzer = LichessAnalyzer(token)
# ... analyze games
```

## Troubleshooting

### "Failed to import game"
- Check your internet connection
- Verify your Lichess token is valid
- Ensure the PGN format is correct

### "Analysis timeout"
- Lichess servers might be busy
- Try again later or reduce number of games

### "No token found"
- Ensure LICHESS_TOKEN is in .env file
- Check environment variable is loaded

## Future Enhancements

Planned features:
- [ ] Puzzle generation from your mistakes
- [ ] Tournament performance analysis
- [ ] Time management analysis
- [ ] Opponent preparation tools
- [ ] Endgame pattern recognition
- [ ] Pawn structure analysis

## Contributing

Feel free to suggest improvements or report issues:
https://github.com/sergi039/sschess/issues

## Privacy Note

- Your games are already public on Chess.com
- Lichess analysis is done via their public API
- No personal data beyond chess games is processed
- Studies created are unlisted by default

---

*Powered by Lichess API and Chess.com API*