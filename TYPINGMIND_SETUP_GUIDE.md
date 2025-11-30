# TypingMind Setup Guide for Chess Analysis Agent

## Quick Setup (3 Steps)

### Step 1: Configure Agent
1. Go to **Agents** in TypingMind
2. Create new agent "Chess Analysis" (or edit existing)
3. Copy ALL content from `AGENT_SYSTEM_PROMPT.md`
4. Paste into agent's **System Instructions**
5. Save the agent

### Step 2: Connect Knowledge Base
1. Go to **Data Sources** → Add New
2. Choose **GitHub** as source
3. Configure:
   - Repository: `sergi039/sschess`
   - Branch: `main`
   - Folder: `knowledge/` (IMPORTANT: must be knowledge, not data!)
4. Click **Sync Now**
5. Wait for sync to complete

### Step 3: Enable Interactive Canvas Plugin
1. Go to **Plugins** in TypingMind
2. Find **Interactive Canvas**
3. Enable it for your agent
4. Save settings

## Testing the Setup

### Test 1: Check Data Access
Ask the agent: "What games do you have in the knowledge base?"

The agent should respond with information from `games_summary.json`, NOT ask for PGN input.

### Test 2: Analyze Specific Game
Ask: "Show me the game from November 29, 2025"

The agent should:
1. Find the game in games_summary.json
2. Display it with Interactive Canvas
3. Show Lichess-style board with pieces visible

### Test 3: Analysis Features
Ask: "Analyze my recent games and show weaknesses"

The agent should use data from:
- analysis_results.json
- weaknesses.md
- recent_games.md

## Troubleshooting

### Problem: Agent asks for PGN input
**Solution**: Agent can't see knowledge base
- Check Data Sources sync status
- Ensure folder is set to `knowledge/` not `data/`
- Re-sync the repository

### Problem: Chess pieces don't display
**Solution**: CDN links not working
- Check Interactive Canvas is enabled
- Verify agent has the correct CDN links from AGENT_SYSTEM_PROMPT.md
- Test with the test HTML file provided

### Problem: No game data found
**Solution**: Data files missing
1. Run on your computer:
```bash
cd chess-knowledge
python scripts/main.py --skip-fetch
```
2. This will generate all needed files
3. Push to GitHub
4. Re-sync in TypingMind

### Problem: Agent uses Chess.com instead of Lichess
**Solution**: Wrong system prompt
- Re-copy AGENT_SYSTEM_PROMPT.md
- Ensure it says "ONLY Lichess components"
- Look for lichess-pgn-viewer in the code

## How It Works

1. **GitHub Actions** runs daily to fetch and analyze your games
2. **Data is synced** to knowledge/ directory with:
   - games_summary.json (last 50 games)
   - analysis_results.json (statistics)
   - canvas_data.json (for visualization)
3. **Agent reads** these files when you ask questions
4. **Interactive Canvas** displays the chess board in chat

## Available Commands

Ask your agent:
- "Show my game from [date]"
- "Analyze game against [opponent]"
- "What are my weaknesses?"
- "Show my opening repertoire"
- "Display my recent games"
- "What's my current rating?"

## Manual Update

To update games manually:
```bash
# On your computer
cd chess-knowledge
python scripts/main.py --months 1
git add .
git commit -m "Update chess data"
git push
```

Then in TypingMind: Data Sources → Sync Now

## Support

- Repository: https://github.com/sergi039/sschess
- Issues: https://github.com/sergi039/sschess/issues
- Test files: test_lichess_board.html