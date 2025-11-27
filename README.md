# Chess Knowledge Base 🚀

Automated chess performance analysis and knowledge base generation for Chess.com players.

This tool fetches your chess games, analyzes patterns, identifies weaknesses, and generates comprehensive Markdown documentation that can be used with AI assistants like TypingMind.

## Features

- 📥 **Automatic game fetching** from Chess.com API
- 📊 **Comprehensive analysis**: openings, time controls, win rates
- 🔍 **Weakness identification**: problematic openings, time management issues
- 📝 **Markdown documentation**: ready for knowledge base integration
- 🤖 **GitHub Actions automation**: daily updates via cron

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd chess-knowledge
```

### 2. Set up environment

Create a `.env` file with your Chess.com username:

```bash
cp .env.example .env
# Edit .env and add your username
CHESS_USERNAME=YourChessUsername
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the pipeline

```bash
cd scripts
python main.py
```

This will:
1. Fetch all your games from Chess.com
2. Analyze them for patterns and weaknesses
3. Generate Markdown files in the `knowledge/` folder

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

## Generated Files

After running, you'll find:

### Knowledge Base (`knowledge/`)
- `summary.md` - Overall statistics and ratings
- `openings.md` - Opening repertoire analysis
- `weaknesses.md` - Identified areas for improvement
- `recent_games.md` - Last 20 games with details

### Data Files (`data/`)
- `games_cache.json` - All fetched games
- `analysis_results.json` - Analysis results

## GitHub Actions Automation

### Setup

1. Go to your GitHub repository Settings → Secrets and variables → Actions
2. Add a secret named `CHESS_USERNAME` with your Chess.com username
3. The workflow will run daily at 6:00 UTC

### Manual trigger

You can also trigger the workflow manually:
1. Go to Actions → Update Chess Knowledge Base
2. Click "Run workflow"
3. Optionally specify months to fetch or skip fetching

## Integration with TypingMind

1. In TypingMind, add a new Data Source
2. Choose GitHub as the source type
3. Point it to this repository's `knowledge/` folder
4. TypingMind will sync the Markdown files automatically

Now you can ask your AI assistant questions like:
- "What are my weaknesses in chess?"
- "How do I perform with the Sicilian Defense?"
- "What openings should I study?"
- "Show my recent performance trends"

## Project Structure

```
chess-knowledge/
├── scripts/
│   ├── main.py              # Main orchestrator
│   ├── fetch_games.py       # Chess.com API fetcher
│   ├── analyze.py           # Game analysis
│   └── generate_markdown.py # Markdown generator
├── data/
│   ├── games_cache.json    # Cached games
│   └── analysis_results.json
├── knowledge/
│   ├── summary.md
│   ├── openings.md
│   ├── weaknesses.md
│   └── recent_games.md
└── .github/
    └── workflows/
        └── update.yml       # GitHub Actions workflow
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

## Limitations

- Chess.com API is public but rate-limited
- Analysis is statistical (no engine evaluation)
- Opening detection is pattern-based (not using ECO database)

## Future Enhancements

Possible improvements:
- [ ] Stockfish integration for position analysis
- [ ] Opponent analysis and preparation
- [ ] Graphical charts and visualizations
- [ ] Puzzle weakness correlation
- [ ] Tournament performance tracking
- [ ] Comparison with previous periods

## Contributing

Feel free to submit issues and pull requests!

## License

MIT

---

*Built with ❤️ for chess improvement*