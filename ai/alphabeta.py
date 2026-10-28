"""
Minimax with Alpha-Beta Pruning (FR-07).

Maintains alpha (the best value guaranteed to the maximizer) and
beta (the best value guaranteed to the minimizer). Prunes branches
whenever beta <= alpha. Uses strategic move ordering (center -> corners -> edges)
to maximize early cutoffs. Supports depth-limited search with heuristic
evaluation for the Medium difficulty level.
"""

from typing import Tuple, Optional, List, Dict
from game.board import (
    get_ordered_legal_moves,
    make_move,
    check_winner,
    is_full,
    evaluate_heuristic,
)

INF = float("inf")


def alphabeta(
    board: Tuple[str, ...],
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    agent_player: str,
    human_player: str,
    node_counter: List[int],
    max_depth: Optional[int] = None,
) -> float:
    """
    Recursive Alpha-Beta pruning search function.
    
    Args:
        board: Immutable 9-element tuple representing current board.
        depth: Current depth in the search tree.
        alpha: Current alpha threshold (best value guaranteed for maximizer).
        beta: Current beta threshold (best value guaranteed for minimizer).
        is_maximizing: True if agent turn, False if human turn.
        agent_player: AI's mark.
        human_player: Human's mark.
        node_counter: Single-element list tracking nodes evaluated.
        max_depth: Optional depth cutoff for heuristic evaluation (Medium difficulty).
        
    Returns:
        The alpha-beta evaluated score.
    """
    node_counter[0] += 1
    
    # Terminal check
    winner, _ = check_winner(board)
    if winner == agent_player:
        return 10.0 - depth
    elif winner == human_player:
        return float(depth - 10)
    elif is_full(board):
        return 0.0

    # Depth limit for heuristic search (Medium level)
    if max_depth is not None and depth >= max_depth:
        return float(evaluate_heuristic(board, agent_player, human_player))

    ordered_moves = get_ordered_legal_moves(board)

    if is_maximizing:
        best_val = -INF
        for move in ordered_moves:
            val = alphabeta(
                make_move(board, move, agent_player),
                depth + 1,
                alpha,
                beta,
                False,
                agent_player,
                human_player,
                node_counter,
                max_depth,
            )
            best_val = max(best_val, val)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break  # Beta cutoff (pruning)
        return best_val
    else:
        best_val = INF
        for move in ordered_moves:
            val = alphabeta(
                make_move(board, move, human_player),
                depth + 1,
                alpha,
                beta,
                True,
                agent_player,
                human_player,
                node_counter,
                max_depth,
            )
            best_val = min(best_val, val)
            beta = min(beta, best_val)
            if beta <= alpha:
                break  # Alpha cutoff (pruning)
        return best_val


def alphabeta_search(
    board: Tuple[str, ...],
    agent_player: str,
    human_player: str,
    max_depth: Optional[int] = None,
) -> Tuple[Optional[int], int, int]:
    """
    Execute alpha-beta search to select the optimal move for agent_player.
    
    Args:
        board: Current 9-element board state.
        agent_player: Agent symbol ('X' or 'O').
        human_player: Human symbol ('X' or 'O').
        max_depth: Depth limit (None for full search / Hard, 2 for Medium).
        
    Returns:
        Tuple of (best_move, best_score, nodes_evaluated).
    """
    ordered_moves = get_ordered_legal_moves(board)
    if not ordered_moves:
        winner, _ = check_winner(board)
        score = 0
        if winner == agent_player:
            score = 10
        elif winner == human_player:
            score = -10
        return None, score, 1

    node_counter = [1]  # Root node
    best_move: Optional[int] = None
    best_score = -INF
    alpha = -INF
    beta = INF

    for move in ordered_moves:
        next_board = make_move(board, move, agent_player)
        score = alphabeta(
            next_board,
            depth=1,
            alpha=alpha,
            beta=beta,
            is_maximizing=False,
            agent_player=agent_player,
            human_player=human_player,
            node_counter=node_counter,
            max_depth=max_depth,
        )
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)

    return best_move, int(best_score), node_counter[0]


def evaluate_all_moves_alphabeta(
    board: Tuple[str, ...],
    agent_player: str,
    human_player: str,
    max_depth: Optional[int] = None,
) -> Dict[int, int]:
    """
    Compute search values for every legal move from the current board.
    Useful for cell evaluation overlays and analysis.
    
    Returns:
        Dict mapping move index to integer score.
    """
    evaluations: Dict[int, int] = {}
    ordered_moves = get_ordered_legal_moves(board)
    dummy_counter = [0]
    
    for move in ordered_moves:
        next_board = make_move(board, move, agent_player)
        score = alphabeta(
            next_board,
            depth=1,
            alpha=-INF,
            beta=INF,
            is_maximizing=False,
            agent_player=agent_player,
            human_player=human_player,
            node_counter=dummy_counter,
            max_depth=max_depth,
        )
        evaluations[move] = int(score)
        
    return evaluations
