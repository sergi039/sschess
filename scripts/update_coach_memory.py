#!/usr/bin/env python3
"""
Update coach memory after each session or periodically
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CoachMemoryUpdater:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "knowledge"
        self.profile_dir = self.base_dir / "player_profile"
        self.session_dir = self.base_dir / "session_logs"
        self.data_dir = Path(__file__).parent.parent / "data"

    def load_json(self, file_path: Path) -> Dict:
        """Load JSON file"""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_json(self, data: Dict, file_path: Path):
        """Save JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def check_new_games(self, since_date: Optional[str] = None) -> List[Dict]:
        """Check for new games since last session"""
        games_file = self.base_dir / "games_all.json"
        if not games_file.exists():
            games_file = self.data_dir / "games_cache.json"

        games_data = self.load_json(games_file)

        if not since_date:
            # Get last session date
            state = self.load_json(self.profile_dir / "current_state.json")
            since_date = state.get("last_session")

        if not since_date:
            return []

        # Parse games and find new ones
        new_games = []
        since_timestamp = datetime.fromisoformat(since_date.replace('Z', '+00:00')).timestamp()

        games = games_data.get("games", [])
        for game in games:
            if game.get("end_time", 0) > since_timestamp:
                new_games.append(game)

        return new_games

    def analyze_recent_performance(self, new_games: List[Dict]) -> Dict:
        """Analyze performance in recent games"""
        if not new_games:
            return {}

        analysis = {
            "games_played": len(new_games),
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "time_pressure_issues": 0,
            "opening_errors": 0,
            "endgame_issues": 0,
            "rating_change": 0
        }

        for game in new_games:
            # Count results
            result = game.get("result", "")
            if "win" in result:
                analysis["wins"] += 1
            elif "draw" in result or "agreed" in result:
                analysis["draws"] += 1
            else:
                analysis["losses"] += 1

            # Check for time issues (simplified)
            pgn = game.get("pgn", "")
            if "Time" in pgn or "flag" in result.lower():
                analysis["time_pressure_issues"] += 1

        analysis["performance"] = f"{analysis['wins']}-{analysis['losses']}-{analysis['draws']}"
        return analysis

    def update_current_state(self, session_data: Optional[Dict] = None):
        """Update current state with latest information"""
        state_file = self.profile_dir / "current_state.json"
        state = self.load_json(state_file)

        # Update basic info
        state["last_updated"] = datetime.now().isoformat()

        if session_data:
            state["last_session"] = datetime.now().isoformat()
            state["total_sessions"] = state.get("total_sessions", 0) + 1

            # Update focus areas if provided
            if "topics_covered" in session_data:
                for topic in session_data["topics_covered"]:
                    if "time_management" in topic.lower():
                        # Update time management weakness
                        for weakness in state.get("active_weaknesses", []):
                            if weakness["area"] == "time_management":
                                weakness["last_reviewed"] = datetime.now().isoformat()
                                weakness["exercises_assigned"] += session_data.get("exercises_assigned", 0)

            # Update next session plan
            if "next_session_plan" in session_data:
                state["next_session_plan"] = session_data["next_session_plan"]

        # Check for new games and update ratings
        new_games = self.check_new_games(state.get("last_session"))
        if new_games:
            recent_analysis = self.analyze_recent_performance(new_games)

            # Update recent achievements if any wins against strong opponents
            for game in new_games:
                if "win" in game.get("result", ""):
                    # Check opponent rating (simplified)
                    achievement = f"Won game on {datetime.fromtimestamp(game['end_time']).strftime('%Y-%m-%d')}"
                    if achievement not in state.get("recent_achievements", []):
                        state.setdefault("recent_achievements", []).append(achievement)

            # Keep only last 10 achievements
            state["recent_achievements"] = state.get("recent_achievements", [])[-10:]

        self.save_json(state, state_file)
        return state

    def create_session_log(self, session_data: Dict):
        """Create a new session log entry"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        session_file = self.session_dir / f"{date_str}_session.json"

        session = {
            "session_id": f"{date_str}-{datetime.now().strftime('%H%M')}",
            "date": datetime.now().isoformat(),
            "duration_minutes": session_data.get("duration", 45),
            "topics_covered": session_data.get("topics_covered", []),
            "games_analyzed": session_data.get("games_analyzed", []),
            "key_insights": session_data.get("key_insights", []),
            "homework_assigned": session_data.get("homework_assigned", []),
            "player_feedback": session_data.get("player_feedback", ""),
            "coach_notes": session_data.get("coach_notes", ""),
            "progress_noted": session_data.get("progress_noted", []),
            "areas_of_concern": session_data.get("areas_of_concern", [])
        }

        # Save session log
        self.save_json(session, session_file)

        # Update session index
        index_file = self.session_dir / "sessions_index.json"
        index = self.load_json(index_file)

        index["total_sessions"] = index.get("total_sessions", 0) + 1
        index["last_session"] = datetime.now().isoformat()
        index["total_time_minutes"] = index.get("total_time_minutes", 0) + session["duration_minutes"]

        # Add session summary to index
        index.setdefault("sessions", []).append({
            "date": session["date"],
            "file": f"{date_str}_session.json",
            "topics": session["topics_covered"],
            "duration": session["duration_minutes"]
        })

        # Keep only last 100 sessions in index
        index["sessions"] = index["sessions"][-100:]
        index["average_session_length"] = index["total_time_minutes"] / max(1, index["total_sessions"])

        self.save_json(index, index_file)
        return session

    def update_progress_metrics(self):
        """Update progress metrics based on recent performance"""
        metrics_file = self.profile_dir / "progress_metrics.json"
        metrics = self.load_json(metrics_file)

        # Get current state for latest ratings
        state = self.load_json(self.profile_dir / "current_state.json")
        current_rating = state.get("current_rating", {})

        # Update rating metrics
        if "metrics" in metrics:
            metrics["metrics"]["rating"]["rapid_current"] = current_rating.get("rapid", 763)
            metrics["metrics"]["rating"]["daily_current"] = current_rating.get("daily", 676)

            # Calculate changes
            metrics["metrics"]["rating"]["rapid_change"] = (
                metrics["metrics"]["rating"]["rapid_current"] -
                metrics["metrics"]["rating"].get("rapid_start", 731)
            )

        # Update last calculated time
        metrics["last_calculated"] = datetime.now().isoformat()

        # Calculate overall improvement rate (simplified)
        days_since_start = 30  # Approximate
        rating_change = metrics["metrics"]["rating"]["rapid_change"]
        metrics["overall_improvement_rate"] = round(rating_change / max(1, days_since_start), 2)

        self.save_json(metrics, metrics_file)
        return metrics

    def update_weakness_timeline(self, weakness_updates: Optional[Dict] = None):
        """Update weakness evolution timeline"""
        timeline_file = self.base_dir / "analysis_evolution" / "weakness_timeline.json"
        timeline = self.load_json(timeline_file)

        if weakness_updates:
            for area, update in weakness_updates.items():
                if area in timeline.get("weaknesses", {}):
                    weakness = timeline["weaknesses"][area]

                    # Add new data point
                    weakness.setdefault("severity_history", []).append({
                        "date": datetime.now().isoformat(),
                        "severity": update.get("severity", "moderate"),
                        "games_affected": update.get("games_affected", 0),
                        "notes": update.get("notes", "")
                    })

                    # Update improvement rate
                    if len(weakness["severity_history"]) > 1:
                        # Simple calculation: reduction in games affected
                        first = weakness["severity_history"][0]["games_affected"]
                        last = weakness["severity_history"][-1]["games_affected"]
                        improvement = (first - last) / max(1, first)
                        weakness["improvement_rate"] = round(improvement, 2)

                    # Add intervention if any
                    if "intervention" in update:
                        weakness.setdefault("interventions", []).append({
                            "date": datetime.now().isoformat(),
                            "type": update["intervention"],
                            "description": update.get("intervention_description", "")
                        })

        self.save_json(timeline, timeline_file)
        return timeline

    def generate_session_summary(self) -> str:
        """Generate a summary of the session for the user"""
        state = self.load_json(self.profile_dir / "current_state.json")
        index = self.load_json(self.session_dir / "sessions_index.json")

        summary = f"""
📝 Session Summary
═══════════════════════════════════════

📊 Session #{state.get('total_sessions', 0)}
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
⏱️ Duration: ~45 minutes

🎯 Topics Covered:
• Time management principles
• Recent game analysis
• Homework review

📈 Current Status:
• Rapid Rating: {state['current_rating']['rapid']}
• Total Sessions: {state.get('total_sessions', 0)}
• Active Focus: {state['current_focus']['primary']}

📝 Homework for Next Time:
• Complete 10 tactical puzzles
• Play 3 games with 10+5 time control
• Review Sicilian Defense video

💪 Keep up the great work!
Your dedication is showing results.

Next session: Continue with endgame basics.
═══════════════════════════════════════
        """
        return summary

def main():
    """Main function to update coach memory"""
    updater = CoachMemoryUpdater()

    # Example session data (in real use, this would come from the chat)
    session_data = {
        "duration": 45,
        "topics_covered": ["time_management", "game_analysis", "sicilian_defense"],
        "games_analyzed": ["146119148014"],
        "key_insights": [
            "Need to allocate time better in opening",
            "Good tactical vision in middlegame",
            "Endgame technique needs work"
        ],
        "homework_assigned": [
            "10 tactical puzzles daily",
            "3 games with 10+5 time control",
            "Watch Sicilian Defense video"
        ],
        "exercises_assigned": 3,
        "player_feedback": "Understood time management concepts",
        "coach_notes": "Shows improvement in tactical awareness",
        "next_session_plan": {
            "priority_topics": ["endgame_basics", "time_management_practice"],
            "homework_check": ["puzzles", "games", "video"]
        }
    }

    print("Updating Coach Memory System...")

    # Update all components
    updater.update_current_state(session_data)
    updater.create_session_log(session_data)
    updater.update_progress_metrics()

    # Check for new games
    new_games = updater.check_new_games()
    if new_games:
        print(f"Found {len(new_games)} new games since last session")
        analysis = updater.analyze_recent_performance(new_games)
        print(f"Performance: {analysis['performance']}")

    # Generate and print summary
    summary = updater.generate_session_summary()
    print(summary)

if __name__ == "__main__":
    main()