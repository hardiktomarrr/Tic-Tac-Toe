"""
Unit tests for the Tic Tac Toe board rules engine (game/board.py).

Covers:
- Empty board initialization
- Legal move generation
- Immutability of board tuples
- All 8 winning lines for Player X and Player O (3 rows, 3 cols, 2 diagonals)
- Draw detection and terminal state tests
- Open line counting and heuristic evaluation
"""

import pytest
from game.board import (
    create_board,
    get_legal_moves,
    get_ordered_legal_moves,
    make_move,
    check_winner,
    is_full,
    is_terminal,
    count_open_lines,
    evaluate_heuristic,
    EMPTY,
    PLAYER_X,
    PLAYER_O,
    WINNING_LINES,
)


def test_initial_board():
    board = create_board()
    assert len(board) == 9
    assert all(cell == EMPTY for cell in board)
    assert get_legal_moves(board) == list(range(9))
    assert not is_full(board)
    assert not is_terminal(board)
    winner, line = check_winner(board)
    assert winner is None
    assert line is None


def test_board_immutability():
    board1 = create_board()
    board2 = make_move(board1, 4, PLAYER_X)
    assert board1[4] == EMPTY
    assert board2[4] == PLAYER_X
    assert board1 is not board2


def test_invalid_moves():
    board = create_board()
    with pytest.raises(ValueError):
        make_move(board, -1, PLAYER_X)
    with pytest.raises(ValueError):
        make_move(board, 9, PLAYER_X)

    board_with_move = make_move(board, 0, PLAYER_X)
    with pytest.raises(ValueError):
        make_move(board_with_move, 0, PLAYER_O)


@pytest.mark.parametrize("line", WINNING_LINES)
@pytest.mark.parametrize("player", [PLAYER_X, PLAYER_O])
def test_all_8_winning_lines(line, player):
    """Test all 8 winning lines (3 rows, 3 cols, 2 diagonals) for both X and O."""
    cells = [EMPTY] * 9
    for idx in line:
        cells[idx] = player
    board = tuple(cells)

    winner, win_line = check_winner(board)
    assert winner == player
    assert win_line == line
    assert is_terminal(board)


def test_draw_detection():
    # Draw position:
    # X O X
    # X O O
    # O X X
    draw_board = (
        PLAYER_X, PLAYER_O, PLAYER_X,
        PLAYER_X, PLAYER_O, PLAYER_O,
        PLAYER_O, PLAYER_X, PLAYER_X,
    )
    assert is_full(draw_board)
    winner, line = check_winner(draw_board)
    assert winner is None
    assert line is None
    assert is_terminal(draw_board)


def test_move_ordering_priority():
    board = create_board()
    ordered = get_ordered_legal_moves(board)
    # Centre (4) must be first, followed by corners (0,2,6,8), then edges (1,3,5,7)
    assert ordered[0] == 4
    assert set(ordered[1:5]) == {0, 2, 6, 8}
    assert set(ordered[5:]) == {1, 3, 5, 7}


def test_heuristic_open_lines():
    board = create_board()
    # On an empty board, all 8 lines are open to both players
    assert count_open_lines(board, PLAYER_X) == 8
    assert count_open_lines(board, PLAYER_O) == 8
    assert evaluate_heuristic(board, PLAYER_X, PLAYER_O) == 0

    # If X takes center (4), lines blocked for O are:
    # Row 2 (3,4,5), Col 2 (1,4,7), Diag 1 (0,4,8), Diag 2 (2,4,6) = 4 lines blocked
    # So O has 8 - 4 = 4 lines open, X has 8 lines open.
    board_x_center = make_move(board, 4, PLAYER_X)
    assert count_open_lines(board_x_center, PLAYER_X) == 8
    assert count_open_lines(board_x_center, PLAYER_O) == 4
    assert evaluate_heuristic(board_x_center, PLAYER_X, PLAYER_O) == 4
