"""
Plain Minimax search algorithm without pruning (FR-06).

Evaluates the entire game tree down to terminal states to find the
theoretically optimal move. Tracks every visited node to establish
the baseline for measuring pruning savings.
"""

from typing import Tuple, Optional, List, Dict
from game.board import (
    get_legal_moves,
    make_move,
    check_winner,
    is_full,
    is_terminal,
)

INF = float("inf")


def minimax(
    board: Tuple[str, ...],
    depth: int,
    is_maximizing: bool,
    agent_player: str,
    human_player: str,
    node_counter: List[int],
) -> int:
    """
    Recursive Minimax decision function.
    
    Args:
        board: Immutable 9-element tuple representing current board.
        depth: Current depth in the search tree (root children are depth 1).
        is_maximizing: True if it's the agent's turn to maximize, False for human minimizing.
        agent_player: Mark of the AI agent ('X' or 'O').
        human_player: Mark of the human player ('X' or 'O').
        node_counter: Single-element list [count] tracking nodes visited.
        
    Returns:
        The minimax value of the position.
    """
    node_counter[0] += 1
    
    # Terminal evaluations:
    winner, _ = check_winner(board)
    if winner == agent_player:
        return 10 - depth
    elif winner == human_player:
        return depth - 10
    elif is_full(board):
        return 0

    if is_maximizing:
        best_val = -INF
        for move in get_legal_moves(board):
            val = minimax(
                make_move(board, move, agent_player),
                depth + 1,
                False,
                agent_player,
                human_player,
                node_counter,
            )
            if val > best_val:
                best_val = val
        return int(best_val)
    else:
        best_val = INF
        for move in get_legal_moves(board):
            val = minimax(
                make_move(board, move, human_player),
                depth + 1,
                True,
                agent_player,
                human_player,
                node_counter,
            )
            if val < best_val:
                best_val = val
        return int(best_val)


def minimax_search(
    board: Tuple[str, ...],
    agent_player: str,
    human_player: str,
) -> Tuple[Optional[int], int, int]:
    """
    Run plain minimax from the current board state to choose the best move for agent.
    
    Args:
        board: Current 9-element board state.
        agent_player: Agent symbol ('X' or 'O').
        human_player: Human symbol ('X' or 'O').
        
    Returns:
        Tuple of (best_move, best_score, nodes_evaluated).
        If no moves are available, returns (None, terminal_score, 1).
    """
    legal_moves = get_legal_moves(board)
    if not legal_moves:
        winner, _ = check_winner(board)
        score = 0
        if winner == agent_player:
            score = 10
        elif winner == human_player:
            score = -10
        return None, score, 1

    node_counter = [1]  # Count root node
    best_move: Optional[int] = None
    best_score = -INF

    for move in legal_moves:
        next_board = make_move(board, move, agent_player)
        score = minimax(
            next_board,
            depth=1,
            is_maximizing=False,
            agent_player=agent_player,
            human_player=human_player,
            node_counter=node_counter,
        )
        if score > best_score:
            best_score = score
            best_move = move

    return best_move, int(best_score), node_counter[0]


def evaluate_all_moves_minimax(
    board: Tuple[str, ...],
    agent_player: str,
    human_player: str,
) -> Dict[int, int]:
    """
    Compute minimax score for every legal move from the current position.
    Used for FR-13 (visualizing minimax values for all empty cells).
    
    Returns:
        Dict mapping move index to integer minimax score.
    """
    evaluations: Dict[int, int] = {}
    legal_moves = get_legal_moves(board)
    dummy_counter = [0]
    
    for move in legal_moves:
        next_board = make_move(board, move, agent_player)
        score = minimax(
            next_board,
            depth=1,
            is_maximizing=False,
            agent_player=agent_player,
            human_player=human_player,
            node_counter=dummy_counter,
        )
        evaluations[move] = int(score)
        
    return evaluations
