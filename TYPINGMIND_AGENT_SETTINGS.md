# Complete TypingMind Agent Configuration

## 🎯 Agent Basic Settings

### Name
`Chess Coach AI`

### Description
```
Expert chess coach with access to 534 games. Provides personalized analysis, identifies patterns, and creates improvement plans. Uses Lichess components for interactive game display.
```

### Avatar
Use chess-related emoji: ♟️ or 👑

### Model
- Preferred: Claude 3.5 Sonnet or GPT-4
- Temperature: 0.3
- Max tokens: 4000
- Top-p: 0.9

## 📚 Knowledge Base Configuration

### Data Source Setup
1. Go to **Data Sources** → **Add New**
2. Choose **GitHub**
3. Configure:
   - Repository: `sergi039/sschess`
   - Branch: `main`
   - Folder: `knowledge/` (IMPORTANT: not `data/`)
4. Click **Sync Now**

### Files in Knowledge Base
After sync, you should have:
- `games_all.json` (1.9MB) - All 534 games
- `games_index.json` (173KB) - Search index
- `analysis_patterns.json` - Weakness patterns
- `analysis_results.json` - Statistics
- `interactive_canvas_example.md` - Display templates

## 🔌 Required Plugins

### 1. Interactive Canvas
- **Status**: Must be ENABLED
- **Purpose**: Display chess boards
- **Test**: Agent should create visual boards

### 2. Web Search (Optional)
- **Purpose**: Look up opening theory
- **Use case**: Current chess news, tournaments

## 🎨 System Instructions

Use the content from `AGENT_SYSTEM_PROMPT_OPTIMIZED.md`:
1. Copy entire content
2. Paste into **System Instructions** field
3. Save agent

## ⚙️ Advanced Parameters

### Agent Behavior
```json
{
  "response_style": "educational",
  "detail_level": "moderate",
  "personality": "supportive coach",
  "expertise": "chess analysis",
  "data_access": "full knowledge base"
}
```

### Custom Instructions
Add these to enhance responses:

```
# Response Format Rules
- Start with brief summary
- Use bullet points for clarity
- Include game references (#123)
- Always show positions visually
- End with actionable advice

# Chess Notation
- Use algebraic notation (Nf3, e4)
- Mark good moves: !
- Mark mistakes: ?
- Mark blunders: ??
- Mark brilliant: !!

# Visual Preferences
- Dark theme for boards
- Show coordinates
- Enable move arrows
- Display clock times
```

## 🧪 Testing Your Agent

### Test 1: Game Retrieval
**You**: "Show my game from November 29, 2025"

**Expected**:
- Finds game vs Nazirou
- Displays with Interactive Canvas
- Shows Philidor Defense

### Test 2: Pattern Analysis
**You**: "What are my biggest weaknesses?"

**Expected**:
- Lists time management issues
- Shows statistics from all 534 games
- Provides specific examples

### Test 3: Opening Analysis
**You**: "How do I perform in the Sicilian?"

**Expected**:
- Searches all games with Sicilian
- Shows win/loss statistics
- Recommends improvements

### Test 4: Coaching Request
**You**: "Help me improve my endgames"

**Expected**:
- Identifies endgame patterns
- Shows example positions
- Creates practice plan

## 🚀 Quick Commands

Configure these shortcuts:

### `/analyze [date]`
Analyzes game from specific date

### `/weaknesses`
Shows current problem areas

### `/openings`
Displays opening repertoire stats

### `/progress`
Shows improvement over time

### `/coach`
Activates detailed lesson mode

## 🛠️ Troubleshooting

### Issue: "Agent asks for PGN input"
**Fix**: Agent can't see knowledge base
- Re-sync Data Sources
- Check folder is `knowledge/`
- Verify games_all.json exists

### Issue: "Chess pieces don't show"
**Fix**: Interactive Canvas not working
- Enable Interactive Canvas plugin
- Check CDN links in response
- Test with simple HTML first

### Issue: "Can't find games"
**Fix**: Index not loaded
- Check games_index.json exists
- Verify JSON structure
- Look for sync errors

### Issue: "Slow responses"
**Fix**: Loading too much data
- Use games_index.json first
- Only load specific games needed
- Reduce temperature to 0.2

## 📊 Performance Metrics

Track agent effectiveness:

1. **Response Quality**
   - Accuracy of game retrieval
   - Correctness of analysis
   - Relevance of suggestions

2. **User Satisfaction**
   - Clear explanations
   - Helpful visualizations
   - Actionable advice

3. **Technical Performance**
   - Response time
   - Canvas rendering
   - Data accuracy

## 🔄 Maintenance

### Daily
- GitHub Actions updates games automatically

### Weekly
- Check for new games in sync
- Review agent performance

### Monthly
- Update analysis patterns
- Refine system prompts
- Add new training examples

## 💡 Pro Tips

1. **Use Conversation Memory**
   - Agent remembers context
   - Reference previous analyses
   - Build on earlier suggestions

2. **Combine with External Tools**
   - Export PGN for engine analysis
   - Link to Lichess studies
   - Connect to puzzle trainers

3. **Create Learning Paths**
   - Sequential lesson plans
   - Track progress over time
   - Adjust difficulty based on improvement

4. **Leverage Patterns**
   - Agent sees all 534 games
   - Identifies recurring mistakes
   - Suggests targeted practice

## 📝 Example Configuration File

Save this as `agent_config.json`:

```json
{
  "name": "Chess Coach AI",
  "model": "claude-3-sonnet",
  "temperature": 0.3,
  "max_tokens": 4000,
  "system_prompt": "See AGENT_SYSTEM_PROMPT_OPTIMIZED.md",
  "plugins": ["interactive_canvas"],
  "knowledge_base": {
    "source": "github",
    "repo": "sergi039/sschess",
    "folder": "knowledge/"
  },
  "parameters": {
    "response_style": "educational",
    "expertise": "chess_analysis",
    "personality": "supportive"
  }
}
```

## 🎓 Training Examples

Add these to improve accuracy:

### Example 1
**Input**: "My last game"
**Output**: Search games_index.json for most recent date, display with analysis

### Example 2
**Input**: "Why do I lose on time?"
**Output**: Analyze time_control field across games, identify patterns

### Example 3
**Input**: "Best game this month"
**Output**: Filter games by date, sort by accuracy/result, show highest rated

## 🏆 Success Criteria

Your agent is properly configured when:

✅ Never asks for PGN input
✅ Finds games by date/opponent quickly
✅ Displays boards with pieces visible
✅ Provides insights from all 534 games
✅ Gives specific improvement advice
✅ Creates visual analyses
✅ Responds like a supportive coach

---

*Last updated: November 30, 2025*
*Games in database: 534*
*Knowledge base: Full access*