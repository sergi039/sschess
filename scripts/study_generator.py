#!/usr/bin/env python3
"""
Lichess study generator for creating interactive learning materials.

This module creates Lichess studies from analyzed games, providing
interactive training materials with annotations and variations.
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import chess
import chess.pgn
from io import StringIO


class StudyGenerator:
    """Generate Lichess studies for training and analysis."""

    def __init__(self, token: str, cache_dir: str = "data"):
        """
        Initialize study generator.

        Args:
            token: Lichess API token
            cache_dir: Directory for saving study data
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.studies_file = self.cache_dir / "lichess_studies.json"
        self.studies = self._load_studies()

    def _load_studies(self) -> Dict:
        """Load existing studies data."""
        if self.studies_file.exists():
            with open(self.studies_file, 'r') as f:
                return json.load(f)
        return {
            "created_studies": [],
            "last_update": None
        }

    def _save_studies(self):
        """Save studies data to disk."""
        self.studies["last_update"] = datetime.now().isoformat()
        with open(self.studies_file, 'w') as f:
            json.dump(self.studies, f, indent=2)

    def create_study(self, title: str, visibility: str = "unlisted") -> Optional[str]:
        """
        Create a new Lichess study.

        Args:
            title: Study title
            visibility: "public", "unlisted", or "private"

        Returns:
            Study ID if successful
        """
        url = "https://lichess.org/api/study"

        data = {
            "name": title,
            "visibility": visibility
        }

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()

            study_id = result.get("id")
            if study_id:
                self.studies["created_studies"].append({
                    "id": study_id,
                    "title": title,
                    "created": datetime.now().isoformat(),
                    "url": f"https://lichess.org/study/{study_id}"
                })
                self._save_studies()

            return study_id

        except requests.exceptions.RequestException as e:
            print(f"Error creating study: {e}")
            return None

    def add_chapter(self, study_id: str, chapter_name: str, pgn: str,
                    orientation: str = "white", analysis: Dict = None) -> bool:
        """
        Add a chapter to a study.

        Args:
            study_id: Lichess study ID
            chapter_name: Name for the chapter
            pgn: PGN content with annotations
            orientation: Board orientation ("white" or "black")
            analysis: Optional analysis data to add as comments

        Returns:
            True if successful
        """
        url = f"https://lichess.org/api/study/{study_id}/chapter"

        # Add analysis as comments to PGN if provided
        if analysis:
            pgn = self._add_analysis_to_pgn(pgn, analysis)

        data = {
            "name": chapter_name,
            "pgn": pgn,
            "orientation": orientation
        }

        try:
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            time.sleep(0.5)  # Rate limiting
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error adding chapter: {e}")
            return False

    def _add_analysis_to_pgn(self, pgn: str, analysis: Dict) -> str:
        """Add analysis comments to PGN."""
        try:
            game = chess.pgn.read_game(StringIO(pgn))
            if not game:
                return pgn

            # Add game-level comment with overall analysis
            if "accuracy" in analysis:
                game.comment = f"Accuracy: {analysis['accuracy']}%"

            # Add move-level comments for mistakes and blunders
            node = game
            move_num = 0

            for move in game.mainline():
                move_num += 1

                # Check if this move is in the analysis
                for blunder in analysis.get("blunders", []):
                    if blunder.get("move_number", 0) == (move_num + 1) // 2:
                        node = node.add_variation(move)
                        node.comment = f"Blunder! Loses {blunder['eval_loss']} centipawns"
                        break
                else:
                    for mistake in analysis.get("mistakes", []):
                        if mistake.get("move_number", 0) == (move_num + 1) // 2:
                            node = node.add_variation(move)
                            node.comment = f"Mistake. Loses {mistake['eval_loss']} centipawns"
                            break
                    else:
                        node = node.add_variation(move)

            # Convert back to PGN string
            output = StringIO()
            exporter = chess.pgn.FileExporter(output)
            game.accept(exporter)
            return output.getvalue()

        except Exception as e:
            print(f"Error adding analysis to PGN: {e}")
            return pgn

    def create_opening_study(self, username: str, games: List[Dict],
                            opening_analysis: Dict) -> Optional[str]:
        """
        Create a study focused on opening preparation.

        Args:
            username: Player's username
            games: List of games
            opening_analysis: Opening analysis data

        Returns:
            Study URL if successful
        """
        title = f"{username}'s Opening Repertoire Study"
        study_id = self.create_study(title)

        if not study_id:
            return None

        # Group games by opening
        openings = {}
        for game in games[:50]:  # Limit to 50 games
            eco = game.get("eco", "Unknown")
            if eco not in openings:
                openings[eco] = []
            openings[eco].append(game)

        # Create chapters for each opening
        for eco, opening_games in openings.items():
            if len(opening_games) >= 3:  # Only include openings with 3+ games
                # Create a chapter with the best game from this opening
                best_game = self._select_best_game(opening_games, username)
                if best_game:
                    chapter_name = f"Opening {eco} - {len(opening_games)} games"

                    # Add opening statistics as comments
                    pgn = best_game.get("pgn", "")
                    if pgn:
                        pgn = self._add_opening_comments(pgn, eco, opening_games, username)
                        self.add_chapter(study_id, chapter_name, pgn)

        return f"https://lichess.org/study/{study_id}"

    def _select_best_game(self, games: List[Dict], username: str) -> Optional[Dict]:
        """Select the best game from a list for demonstration."""
        # Prefer wins, then draws, then losses
        for game in games:
            white = game.get("white", {}).get("username", "").lower()
            if white == username.lower():
                result = game.get("white", {}).get("result", "")
            else:
                result = game.get("black", {}).get("result", "")

            if "win" in result:
                return game

        # If no wins, return the first game
        return games[0] if games else None

    def _add_opening_comments(self, pgn: str, eco: str, games: List[Dict],
                              username: str) -> str:
        """Add opening-specific comments to PGN."""
        try:
            game = chess.pgn.read_game(StringIO(pgn))
            if not game:
                return pgn

            # Calculate statistics for this opening
            wins = sum(1 for g in games if self._did_player_win(g, username))
            total = len(games)
            win_rate = (wins / total * 100) if total > 0 else 0

            # Add header comment
            game.comment = (f"Opening {eco}\n"
                          f"Played {total} times\n"
                          f"Win rate: {win_rate:.1f}%")

            # Convert back to PGN
            output = StringIO()
            exporter = chess.pgn.FileExporter(output)
            game.accept(exporter)
            return output.getvalue()

        except Exception:
            return pgn

    def _did_player_win(self, game: Dict, username: str) -> bool:
        """Check if player won the game."""
        white = game.get("white", {}).get("username", "").lower()
        if white == username.lower():
            return "win" in game.get("white", {}).get("result", "")
        else:
            return "win" in game.get("black", {}).get("result", "")

    def create_tactics_study(self, username: str, tactical_patterns: List[Dict]) -> Optional[str]:
        """
        Create a study with tactical patterns from games.

        Args:
            username: Player's username
            tactical_patterns: List of tactical patterns found

        Returns:
            Study URL if successful
        """
        title = f"{username}'s Tactical Patterns"
        study_id = self.create_study(title)

        if not study_id:
            return None

        # Group patterns by type
        patterns_by_type = {}
        for pattern in tactical_patterns:
            pattern_type = pattern.get("type", "unknown")
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            patterns_by_type[pattern_type].append(pattern)

        # Create chapters for each pattern type
        for pattern_type, patterns in patterns_by_type.items():
            if len(patterns) >= 2:  # Only include pattern types with 2+ examples
                chapter_name = f"{pattern_type.replace('_', ' ').title()} ({len(patterns)} examples)"

                # Create a PGN with the pattern positions
                pgn = self._create_pattern_pgn(patterns[:5])  # Limit to 5 examples
                if pgn:
                    self.add_chapter(study_id, chapter_name, pgn)

        return f"https://lichess.org/study/{study_id}"

    def _create_pattern_pgn(self, patterns: List[Dict]) -> str:
        """Create a PGN demonstrating tactical patterns."""
        # For now, create a simple PGN with comments
        # In a full implementation, this would create puzzle positions
        pgn_lines = ['[Event "Tactical Patterns"]', '[Site "?"]', '[Date "????.??.??"]',
                    '[Round "?"]', '[White "Pattern"]', '[Black "Example"]',
                    '[Result "*"]', '', '']

        # Add a comment describing the patterns
        comments = []
        for pattern in patterns:
            comments.append(f"Move {pattern.get('move_number', '?')}: {pattern.get('description', '')}")

        pgn_lines.append(f"{{ {' | '.join(comments)} }} *")

        return "\n".join(pgn_lines)

    def create_improvement_study(self, username: str, games_analysis: List[Dict],
                                recommendations: List[str]) -> Optional[str]:
        """
        Create a study focused on improvement areas.

        Args:
            username: Player's username
            games_analysis: Analysis of multiple games
            recommendations: List of improvement recommendations

        Returns:
            Study URL if successful
        """
        title = f"{username}'s Improvement Plan"
        study_id = self.create_study(title)

        if not study_id:
            return None

        # Chapter 1: Overview and recommendations
        overview_pgn = self._create_overview_pgn(recommendations)
        self.add_chapter(study_id, "Improvement Overview", overview_pgn)

        # Chapter 2-N: Games with most mistakes/blunders for learning
        games_by_mistakes = sorted(
            games_analysis,
            key=lambda x: len(x.get("analysis", {}).get("blunders", [])) +
                         len(x.get("analysis", {}).get("mistakes", [])),
            reverse=True
        )

        for i, game_analysis in enumerate(games_by_mistakes[:5]):  # Top 5 games to learn from
            game_id = game_analysis.get("game_id", f"game_{i}")
            analysis = game_analysis.get("analysis", {})

            # Get the original PGN (this would need to be passed in or fetched)
            # For now, create a placeholder
            pgn = self._create_mistake_review_pgn(game_id, analysis)

            chapter_name = f"Game Review {i+1} - Learn from mistakes"
            self.add_chapter(study_id, chapter_name, pgn, analysis=analysis)

        return f"https://lichess.org/study/{study_id}"

    def _create_overview_pgn(self, recommendations: List[str]) -> str:
        """Create a PGN with improvement recommendations."""
        pgn_lines = [
            '[Event "Improvement Overview"]',
            '[Site "?"]',
            '[Date "????.??.??"]',
            '[Round "?"]',
            '[White "Recommendations"]',
            '[Black "Focus Areas"]',
            '[Result "*"]',
            '',
            ''
        ]

        # Add recommendations as a comment
        comment_text = "IMPROVEMENT PLAN:\\n\\n"
        for i, rec in enumerate(recommendations, 1):
            comment_text += f"{i}. {rec}\\n"

        pgn_lines.append(f"{{ {comment_text} }} *")

        return "\n".join(pgn_lines)

    def _create_mistake_review_pgn(self, game_id: str, analysis: Dict) -> str:
        """Create a PGN for reviewing mistakes."""
        pgn_lines = [
            f'[Event "Mistake Review - {game_id}"]',
            '[Site "?"]',
            '[Date "????.??.??"]',
            '[Round "?"]',
            '[White "?"]',
            '[Black "?"]',
            '[Result "*"]',
            '',
            ''
        ]

        # Add analysis summary as comment
        accuracy = analysis.get("accuracy", 0)
        blunders = len(analysis.get("blunders", []))
        mistakes = len(analysis.get("mistakes", []))

        comment = f"Accuracy: {accuracy}% | Blunders: {blunders} | Mistakes: {mistakes}"
        pgn_lines.append(f"{{ {comment} }} *")

        return "\n".join(pgn_lines)

    def generate_study_links(self) -> Dict:
        """
        Generate links to all created studies.

        Returns:
            Dictionary of study links
        """
        return {
            "studies": self.studies["created_studies"],
            "total_studies": len(self.studies["created_studies"]),
            "last_update": self.studies.get("last_update")
        }


def main():
    """Test the study generator."""
    token = os.environ.get("LICHESS_TOKEN")
    if not token:
        print("Please set LICHESS_TOKEN environment variable")
        return

    generator = StudyGenerator(token)

    # Test creating a study
    study_id = generator.create_study("Test Study from Chess Knowledge Base")
    if study_id:
        print(f"Created study: https://lichess.org/study/{study_id}")

        # Add a sample chapter
        sample_pgn = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 { Spanish Opening } 1-0"""

        success = generator.add_chapter(study_id, "Test Chapter", sample_pgn)
        if success:
            print("Added chapter successfully")
    else:
        print("Failed to create study")


if __name__ == "__main__":
    main()