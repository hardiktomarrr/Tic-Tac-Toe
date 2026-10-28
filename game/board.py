"""
Board representation and game rules engine for Tic-Tac-Toe.

The board is represented as an immutable 9-element tuple of strings:
' ' for empty cells, 'X', or 'O'.
Indices are mapped as:
 0 | 1 | 2
---+---+---
 3 | 4 | 5
---+---+---
 6 | 7 | 8
"""

from typing import Tuple, List, Optional

EMPTY: str = ' '
PLAYER_X: str = 'X'
PLAYER_O: str = 'O'

# All 8 possible winning lines (3 horizontal, 3 vertical, 2 diagonal)
WINNING_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),  # Row 1
    (3, 4, 5),  # Row 2
    (6, 7, 8),  # Row 3
    (0, 3, 6),  # Col 1
    (1, 4, 7),  # Col 2
    (2, 5, 8),  # Col 3
    (0, 4, 8),  # Main diagonal
    (2, 4, 6),  # Anti diagonal
)

# Standard move ordering priority for Alpha-Beta pruning:
# Centre first, then corners, then edges
PREFERRED_MOVE_ORDER: Tuple[int, ...] = (4, 0, 2, 6, 8, 1, 3, 5, 7)


def create_board() -> Tuple[str, ...]:
    """Create a new, empty 3x3 board represented as a 9-element tuple."""
    return (EMPTY,) * 9


def get_legal_moves(board: Tuple[str, ...]) -> List[int]:
    """
    Return a list of integer indices (0-8) representing empty cells.
    
    Args:
        board: Immutable 9-element tuple representing the board state.
        
    Returns:
        List of legal cell indices where moves can be made.
    """
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def get_ordered_legal_moves(board: Tuple[str, ...]) -> List[int]:
    """
    Return legal moves ordered by strategic priority (center, corners, edges).
    This dramatically improves alpha-beta cutoff efficiency.
    
    Args:
        board: Immutable 9-element tuple representing the board state.
        
    Returns:
        Ordered list of legal move indices.
    """
    return [move for move in PREFERRED_MOVE_ORDER if board[move] == EMPTY]


def make_move(board: Tuple[str, ...], index: int, player: str) -> Tuple[str, ...]:
    """
    Return a new board state with player's mark placed at index.
    The original board is unchanged due to immutability.
    
    Args:
        board: Current board state.
        index: Target cell index (0-8).
        player: 'X' or 'O'.
        
    Returns:
        New 9-element tuple with the move applied.
        
    Raises:
        ValueError: If index is invalid or the cell is already occupied.
    """
    if not (0 <= index < 9):
        raise ValueError(f"Invalid cell index: {index}. Must be 0-8.")
    if board[index] != EMPTY:
        raise ValueError(f"Cell {index} is already occupied by '{board[index]}'.")
    
    board_list = list(board)
    board_list[index] = player
    return tuple(board_list)


def check_winner(board: Tuple[str, ...]) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
    """
    Check if either player has won the game.
    
    Args:
        board: Current board state.
        
    Returns:
        Tuple of (winner_mark, winning_line_tuple).
        If no winner, returns (None, None).
    """
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def is_full(board: Tuple[str, ...]) -> bool:
    """Return True if all 9 cells are occupied, False otherwise."""
    return EMPTY not in board


def is_terminal(board: Tuple[str, ...]) -> bool:
    """
    Return True if the game has ended (either won or drawn).
    
    Args:
        board: Current board state.
        
    Returns:
        True if terminal state, False otherwise.
    """
    winner, _ = check_winner(board)
    return winner is not None or is_full(board)


def get_other_player(player: str) -> str:
    """Return the opponent player symbol ('O' for 'X', 'X' for 'O')."""
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def count_open_lines(board: Tuple[str, ...], player: str) -> int:
    """
    Count how many winning lines (out of 8) are still available to the given player.
    A line is open to a player if none of its 3 cells contain the opponent's mark.
    
    Used in heuristic evaluation for depth-limited search (Medium level).
    
    Args:
        board: Current board state.
        player: Player symbol ('X' or 'O').
        
    Returns:
        Number of open lines (0 to 8).
    """
    opponent = get_other_player(player)
    open_count = 0
    for a, b, c in WINNING_LINES:
        cells = (board[a], board[b], board[c])
        if opponent not in cells:
            open_count += 1
    return open_count


def evaluate_heuristic(board: Tuple[str, ...], agent_player: str, human_player: str) -> int:
    """
    Compute heuristic score for non-terminal positions (e.g., depth-limited Medium search).
    Score = (lines still open to agent) - (lines still open to human).
    
    Args:
        board: Current board state.
        agent_player: AI's mark.
        human_player: Human's mark.
        
    Returns:
        Integer heuristic value.
    """
    return count_open_lines(board, agent_player) - count_open_lines(board, human_player)
