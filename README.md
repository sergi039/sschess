# ♟️ Chess Knowledge Base

Automated chess game analysis system with Chess.com, Lichess, and TypingMind integration.

## 🎯 Key Features

### Basic Analysis (Chess.com) - Daily
- 📊 **Automatic game updates** every day via GitHub Actions
- 📈 **Statistics**: rating, win rate, time control results
- 🎲 **Opening analysis**: repertoire, win percentages, problematic lines
- 📝 **Weakness identification**: error patterns, time management issues
- ⚡ **Fast execution**: < 1 minute for full cycle

### Advanced Analysis (Lichess) - On Request
- 🖥️ **Computer analysis** with Stockfish (accuracy, mistakes, blunders)
- 🎯 **Tactical patterns**: forks, pins, discovered attacks
- 📚 **Lichess opening database**: comparison with master statistics
- 📖 **Interactive Studies**: automatic creation of training materials
- 📊 **Improvement plan**: personalized recommendations based on analysis

### On-Demand Analysis (TypingMind Integration)
- 💬 **AI chat commands**: "Analyze my game from November 29"
- 🔍 **Smart search**: by date, opponent, opening
- 🤖 **Stockfish analysis**: detailed move-by-move breakdown
- 📄 **Lichess-style reports**: accuracy, evaluation graph, critical moments

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/sergi039/sschess.git chess-knowledge
cd chess-knowledge
```

### 2. Install dependencies

```bash
pip install requests python-chess
brew install stockfish  # for macOS (optional, for full analysis)
```

### 3. Configure environment

Create a `.env` file:

```bash
CHESS_USERNAME=sergioquesadas  # your Chess.com username
LICHESS_TOKEN=lip_YourToken    # Lichess token (optional)
```

### 4. Run analysis

```bash
# Basic analysis (fast, ~30 sec)
python scripts/main.py

# With Lichess computer analysis (slower, ~5 min)
python scripts/main.py --enable-lichess

# Analyze specific game
python scripts/analyze_game_on_demand.py "2025-11-29"
```

## Usage Options

### Basic usage (reads from .env)
```bash
python scripts/main.py
```

### Specify username directly
```bash
python scripts/main.py --username YourChessUsername
```

### Fetch only recent games (e.g., last 6 months)
```bash
python scripts/main.py --months 6
```

### Skip fetching (use existing cache)
```bash
python scripts/main.py --skip-fetch
```

## 📁 Generated Files

### Basic Reports (`knowledge/`) - Always Generated
- `summary.md` - Overall statistics and ratings
- `openings.md` - Opening repertoire analysis
- `weaknesses.md` - Identified weaknesses and recommendations
- `recent_games.md` - Last 20 games with details
- `typingmind_commands.md` - Commands for AI chat

### Advanced Reports (with --enable-lichess)
- `lichess_accuracy.md` - Game accuracy and computer evaluation
- `lichess_mistakes.md` - Detailed analysis of mistakes and blunders
- `lichess_tactics.md` - Found tactical patterns
- `lichess_openings.md` - Comparison with Lichess opening database
- `lichess_improvement.md` - Personalized training plan
- `lichess_studies.md` - Links to interactive lessons

### Data Files (`data/`)
- `games_cache.json` - All downloaded games
- `analysis_results.json` - Basic analysis results
- `lichess_analysis_cache.json` - Computer analysis cache
- `detailed_analysis_cache.json` - On-demand analysis cache

## 🤖 GitHub Actions Automation

### Setting up secrets

1. Settings → Secrets and variables → Actions
2. Add secrets:
   - `CHESS_USERNAME` - your Chess.com username
   - `LICHESS_TOKEN` - Lichess token (optional)
3. Workflow runs automatically every day at 6:00 UTC

### Manual run with parameters

1. Actions → Update Chess Knowledge Base → Run workflow
2. Parameters:
   - **months** - number of months to fetch
   - **skip_fetch** - skip fetching new games
   - **enable_lichess** - enable Lichess analysis ✅

## 💬 TypingMind Integration

### Connecting Knowledge Base

1. In TypingMind: Data Sources → Add New
2. Choose GitHub as source
3. Specify repository and `knowledge/` folder
4. TypingMind will automatically sync files

### Available chat commands

**Basic statistics** (always up-to-date):
- "Show my current rating"
- "What are my weak openings?"
- "Show recent games"
- "What are my main problems?"

**Specific game analysis** (requires scripts):
- "Analyze my game from November 29"
- "Find mistakes in game against [opponent]"
- "Show computer evaluation of last game"

**Improvement recommendations**:
- "What should I practice?"
- "Which tactical patterns am I missing?"
- "Training plan for the week"

## 📂 Project Structure

```
chess-knowledge/
├── scripts/
│   ├── main.py                    # Main orchestrator
│   ├── fetch_games.py              # Chess.com game fetching
│   ├── analyze.py                  # Basic analysis
│   ├── generate_markdown.py        # Report generator
│   ├── lichess_analyzer.py         # Computer analysis
│   ├── tactical_detector.py        # Tactical pattern search
│   ├── opening_database.py         # Opening database handling
│   ├── study_generator.py          # Lichess Studies creation
│   ├── generate_lichess_markdown.py # Lichess reports
│   └── analyze_game_on_demand.py   # On-demand analysis
├── knowledge/                      # Markdown files for TypingMind
│   ├── summary.md                  # Overall statistics
│   ├── openings.md                 # Openings
│   ├── weaknesses.md               # Weaknesses
│   ├── recent_games.md             # Recent games
│   ├── lichess_*.md                # Lichess reports (6 files)
│   └── typingmind_commands.md      # Command reference
├── data/                           # Cached data
│   ├── games_cache.json            # All games
│   ├── analysis_results.json       # Analysis results
│   └── *_cache.json                # Various caches
└── .github/
    └── workflows/
        └── update.yml              # GitHub Actions automation
```

## How It Works

1. **Fetching**: Uses Chess.com's public API to download games
   - Incremental updates (only fetches new games)
   - Caches all games locally
   - Rate-limited to respect API guidelines

2. **Analysis**: Processes games to find:
   - Opening repertoire and success rates
   - Performance by time control
   - Time management issues
   - Rating progression
   - Common patterns and weaknesses

3. **Generation**: Creates readable Markdown with:
   - Tables and statistics
   - Specific recommendations
   - Visual indicators (🟢🟡🔴)
   - Links to actual games

## ⚙️ Technical Details

### APIs Used
- **Chess.com API** - game fetching (public, no token required)
- **Lichess API** - computer analysis (requires token)
- **Stockfish** - local engine for deep analysis

### Limitations
- Chess.com API has rate limits (0.5 sec between requests)
- Lichess analysis limited to 5 games at a time
- Stockfish requires local installation for full analysis

## 🚧 Development Roadmap

- [x] Basic game analysis
- [x] Lichess integration
- [x] On-demand analysis from TypingMind
- [x] Tactical patterns
- [x] Opening database
- [ ] Graphs and visualization
- [ ] Opponent analysis
- [ ] Puzzle rating correlation
- [ ] Tournament statistics

## 📖 Documentation

- [LICHESS_README.md](LICHESS_README.md) - Detailed Lichess integration documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [knowledge/typingmind_commands.md](knowledge/typingmind_commands.md) - TypingMind command reference

## 🤝 Contributing

Issues and pull requests are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📄 License

MIT

## 👤 Contact

- GitHub: [@sergi039](https://github.com/sergi039)
- Chess.com: [sergioquesadas](https://www.chess.com/member/sergioquesadas)
- Repository: [github.com/sergi039/sschess](https://github.com/sergi039/sschess)

---

*🚀 Automated chess game analysis system with AI integration*

*Built with Claude Code & ❤️ for chess improvement*