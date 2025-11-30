#!/usr/bin/env python3
"""
Advanced tactical pattern detection for chess games.

This module identifies various tactical themes and patterns in chess games
to help players understand their tactical strengths and weaknesses.
"""

import chess
import chess.pgn
from io import StringIO
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class TacticalDetector:
    """Detects tactical patterns and themes in chess games."""

    def __init__(self):
        """Initialize the tactical detector."""
        self.pattern_counts = defaultdict(int)
        self.pattern_positions = defaultdict(list)

    def analyze_game_tactics(self, pgn: str, game_id: str = "") -> Dict:
        """
        Analyze a game for tactical patterns.

        Args:
            pgn: PGN string of the game
            game_id: Identifier for the game

        Returns:
            Dictionary of tactical patterns found
        """
        try:
            game = chess.pgn.read_game(StringIO(pgn))
            if not game:
                return {}

            board = game.board()
            tactics_found = []
            move_number = 0

            for move in game.mainline_moves():
                move_number += 1
                color = "white" if board.turn else "black"

                # Check various tactical patterns before making the move
                pre_move_tactics = self._check_pre_move_patterns(board, move, move_number, color)
                tactics_found.extend(pre_move_tactics)

                # Make the move
                board.push(move)

                # Check post-move patterns
                post_move_tactics = self._check_post_move_patterns(board, move, move_number, color)
                tactics_found.extend(post_move_tactics)

            return {
                "game_id": game_id,
                "total_tactics": len(tactics_found),
                "tactics": tactics_found,
                "tactical_summary": self._summarize_tactics(tactics_found)
            }

        except Exception as e:
            print(f"Error analyzing tactics for game {game_id}: {e}")
            return {}

    def _check_pre_move_patterns(self, board: chess.Board, move: chess.Move,
                                  move_num: int, color: str) -> List[Dict]:
        """Check for tactical patterns before a move is made."""
        patterns = []

        # Check if this move creates discovered attack
        if self._is_discovered_attack(board, move):
            patterns.append({
                "type": "discovered_attack",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": "Discovered attack"
            })

        # Check for sacrifices
        if self._is_sacrifice(board, move):
            patterns.append({
                "type": "sacrifice",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": f"Piece sacrifice on {chess.square_name(move.to_square)}"
            })

        return patterns

    def _check_post_move_patterns(self, board: chess.Board, move: chess.Move,
                                   move_num: int, color: str) -> List[Dict]:
        """Check for tactical patterns after a move is made."""
        patterns = []

        # Fork detection
        if self._is_fork(board, move):
            forked_pieces = self._get_forked_pieces(board, move.to_square)
            patterns.append({
                "type": "fork",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": f"Fork attacking {', '.join(forked_pieces)}"
            })

        # Pin detection
        pin_info = self._detect_pins(board, move.to_square)
        if pin_info:
            patterns.append({
                "type": "pin",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": pin_info
            })

        # Skewer detection
        skewer_info = self._detect_skewer(board, move.to_square)
        if skewer_info:
            patterns.append({
                "type": "skewer",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": skewer_info
            })

        # Back rank weakness
        if self._is_back_rank_threat(board, move):
            patterns.append({
                "type": "back_rank",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": "Back rank threat"
            })

        # Double attack
        if self._is_double_attack(board, move.to_square):
            patterns.append({
                "type": "double_attack",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": "Double attack"
            })

        # Trapped piece
        if self._has_trapped_piece(board):
            patterns.append({
                "type": "trapped_piece",
                "move_number": (move_num + 1) // 2,
                "color": color,
                "move": str(move),
                "description": "Piece trapped"
            })

        # Check patterns
        if board.is_check():
            # Checkmate
            if board.is_checkmate():
                patterns.append({
                    "type": "checkmate",
                    "move_number": (move_num + 1) // 2,
                    "color": color,
                    "move": str(move),
                    "description": "Checkmate!"
                })
            else:
                patterns.append({
                    "type": "check",
                    "move_number": (move_num + 1) // 2,
                    "color": color,
                    "move": str(move),
                    "description": "Check"
                })

        return patterns

    def _is_fork(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if a move creates a fork."""
        piece = board.piece_at(move.to_square)
        if not piece:
            return False

        # Get all squares attacked by the piece
        attacks = board.attacks(move.to_square)

        # Count valuable pieces being attacked
        valuable_targets = 0
        for square in attacks:
            target = board.piece_at(square)
            if target and target.color != piece.color:
                # Count queens, rooks, bishops, and knights as valuable
                if target.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    valuable_targets += 1
                # Also count the king
                elif target.piece_type == chess.KING:
                    valuable_targets += 2  # King counts as extra valuable

        return valuable_targets >= 2

    def _get_forked_pieces(self, board: chess.Board, square: chess.Square) -> List[str]:
        """Get the names of pieces being forked."""
        piece = board.piece_at(square)
        if not piece:
            return []

        forked = []
        attacks = board.attacks(square)

        for attacked_square in attacks:
            target = board.piece_at(attacked_square)
            if target and target.color != piece.color:
                if target.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.KING]:
                    piece_name = chess.piece_name(target.piece_type).capitalize()
                    forked.append(f"{piece_name} on {chess.square_name(attacked_square)}")

        return forked

    def _detect_pins(self, board: chess.Board, moved_to: chess.Square) -> Optional[str]:
        """Detect if a piece creates a pin."""
        piece = board.piece_at(moved_to)
        if not piece:
            return None

        # Only bishops, rooks, and queens can create pins
        if piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            return None

        # Check along the piece's attack rays for pins
        for direction in self._get_piece_directions(piece):
            ray_squares = self._get_ray_squares(board, moved_to, direction)

            if len(ray_squares) >= 2:
                # Check if there's an enemy piece followed by a more valuable piece
                first_piece = None
                second_piece = None

                for sq in ray_squares:
                    target = board.piece_at(sq)
                    if target:
                        if target.color != piece.color:
                            if not first_piece:
                                first_piece = (sq, target)
                            elif not second_piece:
                                second_piece = (sq, target)
                                break

                if first_piece and second_piece:
                    # Check if second piece is more valuable (especially king)
                    if second_piece[1].piece_type == chess.KING:
                        return f"Absolute pin: {chess.piece_name(first_piece[1].piece_type)} on {chess.square_name(first_piece[0])}"
                    elif second_piece[1].piece_type == chess.QUEEN:
                        return f"Relative pin: {chess.piece_name(first_piece[1].piece_type)} on {chess.square_name(first_piece[0])}"

        return None

    def _detect_skewer(self, board: chess.Board, moved_to: chess.Square) -> Optional[str]:
        """Detect if a piece creates a skewer."""
        piece = board.piece_at(moved_to)
        if not piece:
            return None

        # Only bishops, rooks, and queens can create skewers
        if piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            return None

        # Similar to pin detection but looking for high-value piece in front
        for direction in self._get_piece_directions(piece):
            ray_squares = self._get_ray_squares(board, moved_to, direction)

            if len(ray_squares) >= 2:
                pieces_on_ray = []
                for sq in ray_squares:
                    target = board.piece_at(sq)
                    if target and target.color != piece.color:
                        pieces_on_ray.append((sq, target))
                        if len(pieces_on_ray) == 2:
                            break

                if len(pieces_on_ray) == 2:
                    # Check if first piece is more valuable than second (skewer pattern)
                    first_value = self._get_piece_value(pieces_on_ray[0][1].piece_type)
                    second_value = self._get_piece_value(pieces_on_ray[1][1].piece_type)

                    if first_value > second_value:
                        return f"Skewer: {chess.piece_name(pieces_on_ray[0][1].piece_type)} to {chess.piece_name(pieces_on_ray[1][1].piece_type)}"

        return None

    def _is_discovered_attack(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if a move creates a discovered attack."""
        # Simplified: check if moving piece uncovers attack from another piece
        from_square = move.from_square
        piece_moving = board.piece_at(from_square)

        if not piece_moving:
            return False

        # Check if any piece behind the moving piece now has new attacks
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == piece_moving.color and square != from_square:
                # Check if this piece attacks through the vacated square
                if from_square in board.attacks(square):
                    # Make the move temporarily to check new attacks
                    board_copy = board.copy()
                    board_copy.push(move)
                    new_attacks = board_copy.attacks(square)
                    old_attacks = board.attacks(square)

                    # If there are new valuable targets, it's a discovered attack
                    for new_target in new_attacks - old_attacks:
                        target = board_copy.piece_at(new_target)
                        if target and target.color != piece.color:
                            if target.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                                return True

        return False

    def _is_sacrifice(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if a move is a sacrifice."""
        # Check if we're capturing with a more valuable piece
        moving_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)

        if moving_piece and captured_piece:
            moving_value = self._get_piece_value(moving_piece.piece_type)
            captured_value = self._get_piece_value(captured_piece.piece_type)

            # It's a sacrifice if we're giving up more material
            return moving_value > captured_value + 1

        # Also check if we're moving to a square where we'll be captured
        if moving_piece:
            # Check if the destination square is attacked
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_attacked_by(not board.turn, move.to_square):
                # Check if we have adequate defense
                attackers = len(board_copy.attackers(not board.turn, move.to_square))
                defenders = len(board_copy.attackers(board.turn, move.to_square))
                if attackers > defenders:
                    return True

        return False

    def _is_double_attack(self, board: chess.Board, square: chess.Square) -> bool:
        """Check if a piece creates a double attack."""
        piece = board.piece_at(square)
        if not piece:
            return False

        attacks = board.attacks(square)
        valuable_targets = 0

        for target_square in attacks:
            target = board.piece_at(target_square)
            if target and target.color != piece.color:
                # Count undefended pieces or pieces of value
                if not board.is_attacked_by(target.color, target_square):
                    valuable_targets += 1
                elif target.piece_type in [chess.QUEEN, chess.ROOK]:
                    valuable_targets += 1

        return valuable_targets >= 2

    def _is_back_rank_threat(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if there's a back rank threat."""
        piece = board.piece_at(move.to_square)
        if not piece:
            return False

        # Check if piece is rook or queen on 7th/8th rank (or 1st/2nd for black)
        if piece.piece_type in [chess.ROOK, chess.QUEEN]:
            rank = chess.square_rank(move.to_square)
            if piece.color == chess.WHITE and rank >= 6:  # 7th or 8th rank
                # Check if enemy king is on back rank
                enemy_king_square = board.king(chess.BLACK)
                if enemy_king_square and chess.square_rank(enemy_king_square) == 7:
                    return True
            elif piece.color == chess.BLACK and rank <= 1:  # 1st or 2nd rank
                enemy_king_square = board.king(chess.WHITE)
                if enemy_king_square and chess.square_rank(enemy_king_square) == 0:
                    return True

        return False

    def _has_trapped_piece(self, board: chess.Board) -> bool:
        """Check if any piece is trapped."""
        # Check each piece to see if it has very limited or no moves
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.KING:
                # Count legal moves for this piece
                legal_moves = 0
                for move in board.legal_moves:
                    if move.from_square == square:
                        # Check if the move loses material
                        if not self._move_loses_material(board, move):
                            legal_moves += 1

                # If a valuable piece has no good moves, it might be trapped
                if legal_moves == 0 and piece.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    return True

        return False

    def _move_loses_material(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if a move loses material."""
        board_copy = board.copy()

        # Get material value before move
        moving_piece_value = self._get_piece_value(board.piece_at(move.from_square).piece_type)

        # Make the move
        board_copy.push(move)

        # Check if piece can be captured
        if board_copy.is_attacked_by(not board.turn, move.to_square):
            return True

        return False

    def _get_piece_directions(self, piece: chess.Piece) -> List[Tuple[int, int]]:
        """Get movement directions for a piece."""
        if piece.piece_type == chess.BISHOP:
            return [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        elif piece.piece_type == chess.ROOK:
            return [(0, 1), (0, -1), (1, 0), (-1, 0)]
        elif piece.piece_type == chess.QUEEN:
            return [(1, 1), (1, -1), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]
        return []

    def _get_ray_squares(self, board: chess.Board, start: chess.Square,
                         direction: Tuple[int, int]) -> List[chess.Square]:
        """Get squares along a ray from start square."""
        squares = []
        file = chess.square_file(start)
        rank = chess.square_rank(start)

        while True:
            file += direction[0]
            rank += direction[1]

            if 0 <= file <= 7 and 0 <= rank <= 7:
                square = chess.square(file, rank)
                squares.append(square)

                # Stop if we hit a piece
                if board.piece_at(square):
                    if len(squares) < 8:  # Continue a bit further to detect pins/skewers
                        continue
                    else:
                        break
            else:
                break

        return squares

    def _get_piece_value(self, piece_type: int) -> int:
        """Get the value of a piece type."""
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 1000
        }
        return values.get(piece_type, 0)

    def _summarize_tactics(self, tactics: List[Dict]) -> Dict:
        """Summarize tactical patterns found."""
        summary = defaultdict(int)

        for tactic in tactics:
            summary[tactic["type"]] += 1

        return dict(summary)

    def analyze_multiple_games_tactics(self, games: List[Dict]) -> Dict:
        """
        Analyze tactics across multiple games.

        Args:
            games: List of game dictionaries

        Returns:
            Aggregated tactical analysis
        """
        all_tactics = []
        pattern_frequency = defaultdict(int)
        games_with_patterns = defaultdict(set)

        for i, game in enumerate(games[:50]):  # Limit to 50 games
            pgn = game.get("pgn", "")
            if not pgn:
                continue

            game_id = game.get("url", f"game_{i}")
            analysis = self.analyze_game_tactics(pgn, game_id)

            if analysis and analysis.get("tactics"):
                all_tactics.extend(analysis["tactics"])

                for tactic in analysis["tactics"]:
                    pattern_frequency[tactic["type"]] += 1
                    games_with_patterns[tactic["type"]].add(game_id)

        # Calculate statistics
        total_games = min(50, len(games))

        pattern_stats = {}
        for pattern, count in pattern_frequency.items():
            pattern_stats[pattern] = {
                "total_occurrences": count,
                "games_with_pattern": len(games_with_patterns[pattern]),
                "frequency_per_game": round(count / total_games, 2),
                "percentage_of_games": round(len(games_with_patterns[pattern]) / total_games * 100, 1)
            }

        return {
            "total_tactics_found": len(all_tactics),
            "games_analyzed": total_games,
            "pattern_statistics": pattern_stats,
            "most_common_patterns": sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "tactical_richness": round(len(all_tactics) / total_games, 1) if total_games > 0 else 0
        }


def main():
    """Test the tactical detector."""
    detector = TacticalDetector()

    sample_pgn = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O
9. h3 Nb8 10. d4 Nbd7 11. Nbd2 Bb7 12. Bc2 Re8 13. Nf1 Bf8 14. Ng3 g6 15. a4 c5
16. d5 c4 17. Bg5 h6 18. Be3 Nc5 19. Qd2 h5 20. Bg5 Bg7 21. Nh2 Qc7 22. f4 exf4
23. Bxf4 Nh7 24. Rf1 Bf6 25. Ngf1 Bg5 26. Bxg5 Nxg5 27. Ne3 Bc8 28. Nhg4 hxg4
29. hxg4 Kg7 30. Qf4 Rh8 31. Qxd6 Qxd6 32. Rf6 Qe5 33. Raf1 Bd7 34. axb5 axb5
35. R1f5 Qe7 36. Nxc4 bxc4 37. Rxc5 Qd6 38. Rc7 Be8 39. e5 Qb6+ 40. Kf1 Qxb2
41. Bd1 Qb1 42. Ke2 Ra2+ 43. Kf3 Ne6 44. dxe6 1-0"""

    result = detector.analyze_game_tactics(sample_pgn, "test_game")
    print(f"Found {result.get('total_tactics', 0)} tactical patterns")
    if result.get("tactics"):
        for tactic in result["tactics"]:
            print(f"  - {tactic['type']}: {tactic['description']} (move {tactic['move_number']})")


if __name__ == "__main__":
    main()