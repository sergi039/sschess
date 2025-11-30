#!/usr/bin/env python3
"""
Initialize the coach memory system with baseline data
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

def create_directory_structure():
    """Create the necessary directories for coach memory"""
    base_dir = Path(__file__).parent.parent / "knowledge"

    directories = [
        "player_profile",
        "session_logs",
        "learning_paths",
        "analysis_evolution",
        "checkpoints"
    ]

    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")

def initialize_current_state():
    """Create initial current_state.json"""

    current_state = {
        "player_id": "sergioquesadas",
        "last_updated": datetime.now().isoformat(),
        "last_session": None,
        "total_sessions": 0,
        "account_created": "2025-11-15",  # Approximate
        "total_games_analyzed": 534,
        "current_rating": {
            "rapid": 763,
            "daily": 676,
            "trend": "improving",
            "peak_rapid": 763,
            "peak_daily": 676
        },
        "current_focus": {
            "primary": "time_management",
            "secondary": "endgame_technique",
            "opening_work": "sicilian_defense"
        },
        "active_weaknesses": [
            {
                "area": "time_management",
                "severity": "critical",
                "games_affected": 14,
                "improvement_rate": 0.0,
                "first_identified": datetime.now().isoformat(),
                "last_reviewed": None,
                "exercises_assigned": 0,
                "exercises_completed": 0,
                "specific_issues": [
                    "Spending too much time in opening",
                    "Panic in time pressure",
                    "Not using increment effectively"
                ]
            },
            {
                "area": "endgame_conversion",
                "severity": "moderate",
                "games_affected": 8,
                "improvement_rate": 0.0,
                "first_identified": datetime.now().isoformat(),
                "last_reviewed": None,
                "exercises_assigned": 0,
                "exercises_completed": 0,
                "specific_issues": [
                    "Struggling with rook endgames",
                    "Missing winning continuations",
                    "Drawing won positions"
                ]
            },
            {
                "area": "opening_preparation",
                "severity": "moderate",
                "games_affected": 35,
                "improvement_rate": 0.0,
                "first_identified": datetime.now().isoformat(),
                "last_reviewed": None,
                "exercises_assigned": 0,
                "exercises_completed": 0,
                "specific_issues": [
                    "Weak against 1.e4 (42% win rate)",
                    "No repertoire against Sicilian",
                    "Mixing up move orders"
                ]
            }
        ],
        "strengths": [
            {
                "area": "tactical_awareness",
                "level": "intermediate",
                "evidence": "Good combination play in middlegame"
            },
            {
                "area": "fighting_spirit",
                "level": "strong",
                "evidence": "Rarely resigns, fights till the end"
            }
        ],
        "recent_achievements": [],
        "next_session_plan": {
            "priority_topics": [
                "Review time management principles",
                "Analyze recent time pressure losses",
                "Practice rapid decision making"
            ],
            "suggested_exercises": [
                "5+3 blitz session (5 games)",
                "Puzzle rush timed mode",
                "Opening repertoire review"
            ],
            "homework_check": []
        },
        "learning_style": {
            "preferred_format": "game_analysis",
            "attention_span": "moderate",
            "responds_well_to": ["specific_examples", "pattern_recognition"],
            "avoid": ["too_much_theory", "abstract_concepts"]
        }
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "player_profile" / "current_state.json"
    with open(file_path, 'w') as f:
        json.dump(current_state, f, indent=2)
    print(f"Created: {file_path}")

def initialize_training_history():
    """Create initial training_history.json"""

    training_history = {
        "sessions": [],
        "total_training_hours": 0.0,
        "topics_mastered": [],
        "topics_in_progress": [
            "time_management",
            "basic_endgames",
            "sicilian_defense"
        ],
        "topics_planned": [
            "positional_play",
            "pawn_structures",
            "attack_patterns"
        ],
        "homework_completion_rate": 0.0,
        "preferred_session_time": "evening",
        "average_session_duration": 45
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "player_profile" / "training_history.json"
    with open(file_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    print(f"Created: {file_path}")

def initialize_progress_metrics():
    """Create initial progress_metrics.json based on game analysis"""

    progress_metrics = {
        "baseline_date": datetime.now().isoformat(),
        "overall_improvement_rate": 0.0,
        "last_calculated": datetime.now().isoformat(),
        "metrics": {
            "rating": {
                "rapid_start": 731,
                "rapid_current": 763,
                "rapid_change": 32,
                "daily_start": 676,
                "daily_current": 676,
                "daily_change": 0,
                "trend": "improving"
            },
            "tactics": {
                "estimated_rating": 1200,
                "accuracy_rate": None,
                "patterns_recognized": ["forks", "pins", "basic_checkmates"],
                "patterns_learning": ["discovered_attacks", "deflection"]
            },
            "time_management": {
                "avg_time_per_move": 45,
                "time_pressure_losses": 14,
                "games_lost_on_time": 14,
                "improvement_target": "Reduce by 50%"
            },
            "opening_knowledge": {
                "repertoire_size": 5,
                "main_openings": {
                    "white": ["Italian Game", "Scotch Game"],
                    "black": ["Philidor Defense", "Sicilian (learning)"]
                },
                "accuracy_first_10_moves": 0.68,
                "theory_depth": "5-8 moves",
                "problem_openings": ["French Defense", "Caro-Kann"]
            },
            "endgame_skill": {
                "conversion_rate": 0.65,
                "drawn_won_positions": 8,
                "basic_checkmates": "inconsistent",
                "pawn_endgames": "beginner",
                "rook_endgames": "struggling"
            },
            "psychological": {
                "tilt_resistance": "moderate",
                "comeback_ability": "good",
                "pressure_handling": "needs_work"
            }
        },
        "milestones_achieved": [
            {
                "date": (datetime.now() - timedelta(days=10)).isoformat(),
                "achievement": "Reached 750+ rapid rating",
                "category": "rating"
            }
        ],
        "next_milestones": [
            {
                "target": "800 rapid rating",
                "estimated_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "requirements": ["Improve time management", "Solidify openings"]
            },
            {
                "target": "Master basic endgames",
                "estimated_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "requirements": ["Study K+P vs K", "Practice rook endgames"]
            },
            {
                "target": "Complete Sicilian Defense repertoire",
                "estimated_date": (datetime.now() + timedelta(days=60)).isoformat(),
                "requirements": ["Learn main lines", "Practice in games"]
            }
        ],
        "improvement_velocity": {
            "last_30_days": "+32 rating points",
            "projection_next_30": "+25-40 points",
            "limiting_factors": ["time_management", "endgame_technique"]
        }
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "player_profile" / "progress_metrics.json"
    with open(file_path, 'w') as f:
        json.dump(progress_metrics, f, indent=2)
    print(f"Created: {file_path}")

def initialize_curriculum():
    """Create initial learning curriculum"""

    curriculum = {
        "created": datetime.now().isoformat(),
        "level": "advanced_beginner",
        "estimated_rating_range": "700-800",
        "current_module": 1,
        "modules": [
            {
                "id": 1,
                "name": "Foundation Repair",
                "status": "in_progress",
                "started": datetime.now().isoformat(),
                "progress": 0.0,
                "topics": [
                    {
                        "name": "Time Management Fundamentals",
                        "status": "not_started",
                        "lessons": [
                            "Understanding time allocation",
                            "Critical moments identification",
                            "Using increment effectively",
                            "Practical exercises"
                        ]
                    },
                    {
                        "name": "Basic Endgame Patterns",
                        "status": "not_started",
                        "lessons": [
                            "King and Pawn vs King",
                            "Basic checkmates review",
                            "Rook endgame principles",
                            "Practical positions"
                        ]
                    }
                ]
            },
            {
                "id": 2,
                "name": "Opening Consolidation",
                "status": "locked",
                "unlock_criteria": "Complete Foundation Repair",
                "topics": [
                    {
                        "name": "Sicilian Defense for Black",
                        "lessons": [
                            "Basic Sicilian structures",
                            "Dragon variation basics",
                            "Common tactical patterns",
                            "Model games"
                        ]
                    },
                    {
                        "name": "1.e4 repertoire for White",
                        "lessons": [
                            "Italian Game mastery",
                            "Scotch Game improvement",
                            "Anti-Sicilian options"
                        ]
                    }
                ]
            },
            {
                "id": 3,
                "name": "Tactical Sharpening",
                "status": "locked",
                "unlock_criteria": "Complete Opening Consolidation",
                "topics": [
                    "Advanced tactical patterns",
                    "Calculation training",
                    "Defensive tactics",
                    "Tactical endgames"
                ]
            }
        ],
        "recommended_resources": [
            {
                "type": "video",
                "title": "Time Management for Club Players - IM Andras Toth",
                "url": "https://www.youtube.com/watch?v=...",
                "priority": "high",
                "assigned": datetime.now().isoformat(),
                "completed": False
            },
            {
                "type": "interactive",
                "title": "Lichess Endgame Practice",
                "url": "https://lichess.org/practice/basic-checkmates",
                "priority": "high",
                "assigned": datetime.now().isoformat(),
                "completed": False
            },
            {
                "type": "book",
                "title": "The Complete Chess Course by Fred Reinfeld",
                "chapters": "Review chapters 1-3",
                "priority": "medium",
                "progress": "not_started"
            },
            {
                "type": "puzzle_set",
                "title": "Daily Tactical Training",
                "description": "10 puzzles per day on Chess.com or Lichess",
                "priority": "high",
                "streak": 0
            }
        ],
        "study_schedule": {
            "recommended_hours_per_week": 7,
            "distribution": {
                "game_play": "40%",
                "analysis": "30%",
                "puzzles": "20%",
                "theory": "10%"
            }
        }
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "learning_paths" / "current_curriculum.json"
    with open(file_path, 'w') as f:
        json.dump(curriculum, f, indent=2)
    print(f"Created: {file_path}")

def initialize_session_index():
    """Create initial session index"""

    session_index = {
        "total_sessions": 0,
        "last_session": None,
        "sessions": [],
        "total_time_minutes": 0,
        "average_session_length": 0
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "session_logs" / "sessions_index.json"
    with open(file_path, 'w') as f:
        json.dump(session_index, f, indent=2)
    print(f"Created: {file_path}")

def initialize_weakness_timeline():
    """Create initial weakness evolution tracking"""

    weakness_timeline = {
        "tracking_started": datetime.now().isoformat(),
        "weaknesses": {
            "time_management": {
                "severity_history": [
                    {"date": datetime.now().isoformat(), "severity": "critical", "games_affected": 14}
                ],
                "interventions": [],
                "improvement_rate": 0.0
            },
            "endgame_conversion": {
                "severity_history": [
                    {"date": datetime.now().isoformat(), "severity": "moderate", "games_affected": 8}
                ],
                "interventions": [],
                "improvement_rate": 0.0
            },
            "opening_preparation": {
                "severity_history": [
                    {"date": datetime.now().isoformat(), "severity": "moderate", "games_affected": 35}
                ],
                "interventions": [],
                "improvement_rate": 0.0
            }
        },
        "resolved_weaknesses": []
    }

    file_path = Path(__file__).parent.parent / "knowledge" / "analysis_evolution" / "weakness_timeline.json"
    with open(file_path, 'w') as f:
        json.dump(weakness_timeline, f, indent=2)
    print(f"Created: {file_path}")

def main():
    """Initialize all coach memory components"""

    print("Initializing Coach Memory System...")
    print("=" * 50)

    # Create directory structure
    create_directory_structure()

    # Initialize all JSON files
    initialize_current_state()
    initialize_training_history()
    initialize_progress_metrics()
    initialize_curriculum()
    initialize_session_index()
    initialize_weakness_timeline()

    print("=" * 50)
    print("✅ Coach Memory System initialized successfully!")
    print("\nThe system will now:")
    print("• Track all training sessions")
    print("• Monitor progress over time")
    print("• Remember previous conversations")
    print("• Build personalized curriculum")
    print("• Adapt to your learning style")

if __name__ == "__main__":
    main()