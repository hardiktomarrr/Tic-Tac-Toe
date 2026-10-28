"""
AI Agent decision module integrating search strategies and difficulty levels.

Provides high-level decision making for:
- Easy: Random legal move selection
- Medium: Depth-limited (depth=2) Alpha-Beta search with heuristic evaluation
- Hard: Full-depth search (Minimax or Alpha-Beta based on pruning toggle)

Includes move timing via time.perf_counter() and helper utilities for hints
and cell evaluation overlays.
"""

import time
import random
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, List

from game.board import (
    get_legal_moves,
    get_ordered_legal_moves,
)
from ai.minimax import minimax_search, evaluate_all_moves_minimax
from ai.alphabeta import alphabeta_search, evaluate_all_moves_alphabeta

DIFFICULTY_EASY = "Easy"
DIFFICULTY_MEDIUM = "Medium"
DIFFICULTY_HARD = "Hard"


@dataclass
class AgentDecision:
    """Encapsulates the agent's move decision and search statistics."""
    move: Optional[int]
    score: int
    nodes_evaluated: int
    time_taken_ms: float
    algorithm_name: str


def select_agent_move(
    board: Tuple[str, ...],
    agent_player: str,
    human_player: str,
    difficulty: str = DIFFICULTY_HARD,
    use_pruning: bool = True,
) -> AgentDecision:
    """
    Select the agent's next move based on difficulty and pruning settings.
    
    Args:
        board: Immutable 9-element tuple representing current board.
        agent_player: Mark of the AI agent ('X' or 'O').
        human_player: Mark of the human player ('X' or 'O').
        difficulty: One of 'Easy', 'Medium', 'Hard'.
        use_pruning: If True, uses Alpha-Beta pruning; if False, uses Plain Minimax.
        
    Returns:
        AgentDecision containing chosen move, score, node count, and runtime in ms.
    """
    legal_moves = get_legal_moves(board)
    if not legal_moves:
        return AgentDecision(
            move=None,
            score=0,
            nodes_evaluated=1,
            time_taken_ms=0.0,
            algorithm_name="None (No legal moves)",
        )

    start_time = time.perf_counter()

    if difficulty == DIFFICULTY_EASY:
        # Easy: Uniformly pick a random legal move
        move = random.choice(legal_moves)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return AgentDecision(
            move=move,
            score=0,
            nodes_evaluated=1,
            time_taken_ms=elapsed_ms,
            algorithm_name="Random Selection",
        )

    elif difficulty == DIFFICULTY_MEDIUM:
        # Medium: Depth-limited (depth=2) alpha-beta with heuristic
        move, score, nodes = alphabeta_search(
            board,
            agent_player=agent_player,
            human_player=human_player,
            max_depth=2,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return AgentDecision(
            move=move,
            score=score,
            nodes_evaluated=nodes,
            time_taken_ms=elapsed_ms,
            algorithm_name="Alpha-Beta (Depth 2 Heuristic)",
        )

    else:
        # Hard: Full-depth search (unbeatable)
        if use_pruning:
            move, score, nodes = alphabeta_search(
                board,
                agent_player=agent_player,
                human_player=human_player,
                max_depth=None,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return AgentDecision(
                move=move,
                score=score,
                nodes_evaluated=nodes,
                time_taken_ms=elapsed_ms,
                algorithm_name="Alpha-Beta Pruning (Full Depth)",
            )
        else:
            move, score, nodes = minimax_search(
                board,
                agent_player=agent_player,
                human_player=human_player,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return AgentDecision(
                move=move,
                score=score,
                nodes_evaluated=nodes,
                time_taken_ms=elapsed_ms,
                algorithm_name="Plain Minimax (Full Depth)",
            )


def get_hint_move(
    board: Tuple[str, ...],
    human_player: str,
    agent_player: str,
    use_pruning: bool = True,
) -> Optional[int]:
    """
    Suggest the optimal move for the human player (FR-12).
    Runs full-depth search from the human's perspective.
    
    Args:
        board: Current board state.
        human_player: Human player's mark.
        agent_player: Agent's mark.
        use_pruning: Whether to use alpha-beta pruning.
        
    Returns:
        Recommended cell index (0-8) or None if no moves left.
    """
    if use_pruning:
        move, _, _ = alphabeta_search(
            board,
            agent_player=human_player,
            human_player=agent_player,
            max_depth=None,
        )
    else:
        move, _, _ = minimax_search(
            board,
            agent_player=human_player,
            human_player=agent_player,
        )
    return move


def get_cell_minimax_values(
    board: Tuple[str, ...],
    player_turn: str,
    opponent: str,
    use_pruning: bool = True,
) -> Dict[int, int]:
    """
    Compute minimax evaluation values for each empty cell (FR-13).
    A positive score indicates an advantage, 0 indicates a draw, negative is disadvantage.
    
    Returns:
        Dict of {cell_index: score}.
    """
    if use_pruning:
        return evaluate_all_moves_alphabeta(
            board,
            agent_player=player_turn,
            human_player=opponent,
            max_depth=None,
        )
    else:
        return evaluate_all_moves_minimax(
            board,
            agent_player=player_turn,
            human_player=opponent,
        )
