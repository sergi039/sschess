#!/usr/bin/env python3
"""
Fetch chess games from Chess.com API.

This script downloads all games for a specified user from Chess.com
and saves them to a JSON cache file for analysis.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class ChessComFetcher:
    """Fetches games from Chess.com public API."""

    BASE_URL = "https://api.chess.com/pub"

    def __init__(self, username: str, cache_dir: str = "data"):
        """
        Initialize fetcher.

        Args:
            username: Chess.com username
            cache_dir: Directory to store cached data
        """
        self.username = username.lower()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "games_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load existing cache or create empty one."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {
            "username": self.username,
            "last_update": None,
            "games": [],
            "archives_fetched": []
        }

    def _save_cache(self):
        """Save cache to disk."""
        self.cache["last_update"] = datetime.now().isoformat()
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _api_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make API request with rate limiting.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response or None if error
        """
        url = f"{self.BASE_URL}{endpoint}"
        print(f"Fetching: {url}")

        try:
            response = requests.get(url, headers={
                "User-Agent": "ChessKnowledgeBase/1.0"
            })
            response.raise_for_status()

            # Rate limiting - Chess.com asks for reasonable delays
            time.sleep(0.5)

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_player_profile(self) -> Optional[Dict]:
        """
        Fetch player profile and stats.

        Returns:
            Player profile data
        """
        profile = self._api_request(f"/player/{self.username}")
        if profile:
            stats = self._api_request(f"/player/{self.username}/stats")
            if stats:
                profile["stats"] = stats
        return profile

    def fetch_archives(self) -> List[str]:
        """
        Fetch list of available game archives.

        Returns:
            List of archive URLs
        """
        data = self._api_request(f"/player/{self.username}/games/archives")
        if data and "archives" in data:
            return data["archives"]
        return []

    def fetch_games(self, months_back: Optional[int] = None) -> int:
        """
        Fetch all games or games from last N months.

        Args:
            months_back: Number of months to fetch (None = all)

        Returns:
            Number of new games fetched
        """
        # Get list of archives
        archives = self.fetch_archives()
        if not archives:
            print(f"No game archives found for {self.username}")
            return 0

        # Filter by months if specified
        if months_back:
            cutoff_date = datetime.now() - timedelta(days=30 * months_back)
            filtered_archives = []
            for archive_url in archives:
                # Extract year and month from URL
                parts = archive_url.split("/")
                year, month = int(parts[-2]), int(parts[-1])
                archive_date = datetime(year, month, 1)
                if archive_date >= cutoff_date:
                    filtered_archives.append(archive_url)
            archives = filtered_archives

        print(f"Found {len(archives)} archives to process")

        # Fetch games from each archive
        new_games = 0
        current_month = datetime.now().strftime("%Y/%m")

        for archive_url in archives:
            # Always re-fetch current month to get new games
            # Skip other months if already fetched
            if archive_url in self.cache["archives_fetched"] and current_month not in archive_url:
                print(f"Skipping already fetched: {archive_url}")
                continue

            # Fetch archive
            archive_data = self._api_request(archive_url.replace("https://api.chess.com/pub", ""))
            if not archive_data or "games" not in archive_data:
                continue

            # Process games
            for game in archive_data["games"]:
                # Add metadata
                game["fetched_at"] = datetime.now().isoformat()
                game["archive_url"] = archive_url

                # Check if game already exists (by URL)
                if not any(g.get("url") == game.get("url") for g in self.cache["games"]):
                    self.cache["games"].append(game)
                    new_games += 1

            # Mark archive as fetched (but don't mark current month to allow re-fetching)
            if current_month not in archive_url and archive_url not in self.cache["archives_fetched"]:
                self.cache["archives_fetched"].append(archive_url)
            print(f"Fetched {len(archive_data['games'])} games from {archive_url}")

            # Save cache after each archive (in case of interruption)
            self._save_cache()

        return new_games

    def get_summary(self) -> Dict:
        """
        Get summary statistics of fetched games.

        Returns:
            Summary statistics
        """
        total_games = len(self.cache["games"])

        if total_games == 0:
            return {"total_games": 0}

        # Count by time control
        time_controls = {}
        results = {"wins": 0, "losses": 0, "draws": 0}
        colors = {"white": 0, "black": 0}

        for game in self.cache["games"]:
            # Time control
            tc = game.get("time_class", "unknown")
            time_controls[tc] = time_controls.get(tc, 0) + 1

            # Results
            white_player = game.get("white", {}).get("username", "").lower()
            black_player = game.get("black", {}).get("username", "").lower()

            if white_player == self.username:
                colors["white"] += 1
                result = game.get("white", {}).get("result", "")
            elif black_player == self.username:
                colors["black"] += 1
                result = game.get("black", {}).get("result", "")
            else:
                continue

            if "win" in result:
                results["wins"] += 1
            elif result in ["resigned", "timeout", "checkmated", "abandoned"]:
                results["losses"] += 1
            else:
                results["draws"] += 1

        # Get date range
        dates = [game.get("end_time", 0) for game in self.cache["games"]]
        if dates:
            oldest = datetime.fromtimestamp(min(dates)).strftime("%Y-%m-%d")
            newest = datetime.fromtimestamp(max(dates)).strftime("%Y-%m-%d")
        else:
            oldest = newest = "N/A"

        return {
            "total_games": total_games,
            "date_range": f"{oldest} to {newest}",
            "time_controls": time_controls,
            "results": results,
            "colors": colors,
            "win_rate": round(results["wins"] / total_games * 100, 1) if total_games > 0 else 0
        }


def main():
    """Main function to run the fetcher."""
    # Get username from environment or use default
    username = os.environ.get("CHESS_USERNAME", "")
    if not username:
        print("Please set CHESS_USERNAME environment variable or create .env file")
        return

    months = os.environ.get("MONTHS_TO_FETCH")
    months_back = int(months) if months else None

    print(f"Fetching games for: {username}")
    if months_back:
        print(f"Limiting to last {months_back} months")

    # Create fetcher and run
    fetcher = ChessComFetcher(username)

    # Fetch player profile
    print("\n1. Fetching player profile...")
    profile = fetcher.fetch_player_profile()
    if profile:
        print(f"   Player: {profile.get('name', username)}")
        print(f"   Country: {profile.get('country', 'Unknown')}")
        if "stats" in profile:
            stats = profile["stats"]
            for category in ["chess_rapid", "chess_blitz", "chess_bullet"]:
                if category in stats:
                    rating = stats[category]["last"]["rating"]
                    print(f"   {category.replace('chess_', '').title()}: {rating}")

    # Fetch games
    print("\n2. Fetching games...")
    new_games = fetcher.fetch_games(months_back)
    print(f"   Fetched {new_games} new games")

    # Show summary
    print("\n3. Summary:")
    summary = fetcher.get_summary()
    print(f"   Total games: {summary['total_games']}")
    print(f"   Date range: {summary['date_range']}")
    print(f"   Win rate: {summary['win_rate']}%")
    print(f"   Results: W:{summary['results']['wins']} L:{summary['results']['losses']} D:{summary['results']['draws']}")
    print(f"   Colors: White:{summary['colors']['white']} Black:{summary['colors']['black']}")
    print(f"   Time controls: {summary['time_controls']}")

    print(f"\nData saved to: {fetcher.cache_file}")


if __name__ == "__main__":
    main()