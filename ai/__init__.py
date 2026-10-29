"""AI Adversarial Search and Agent package."""
from .minimax import minimax_search, minimax, evaluate_all_moves_minimax
from .alphabeta import alphabeta_search, alphabeta, evaluate_all_moves_alphabeta
from .agent import (
    select_agent_move,
    get_hint_move,
    get_cell_minimax_values,
    AgentDecision,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_RANDOM,
    DIFFICULTY_MINIMAX,
    DIFFICULTY_MEDIUM,
)

__all__ = [
    "minimax_search",
    "minimax",
    "evaluate_all_moves_minimax",
    "alphabeta_search",
    "alphabeta",
    "evaluate_all_moves_alphabeta",
    "select_agent_move",
    "get_hint_move",
    "get_cell_minimax_values",
    "AgentDecision",
    "DIFFICULTY_EASY",
    "DIFFICULTY_HARD",
    "DIFFICULTY_RANDOM",
    "DIFFICULTY_MINIMAX",
    "DIFFICULTY_MEDIUM",
]
