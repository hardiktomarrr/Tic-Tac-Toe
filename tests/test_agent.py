"""
Unit and integration tests for AI adversarial search agents (Minimax and Alpha-Beta).

Acceptance Criteria verified:
1. Alpha-Beta returns the same optimal value as plain Minimax.
2. Alpha-Beta prunes branches and evaluates significantly fewer nodes.
3. Hard agent is unbeatable: 0 losses across games as both Player X and Player O.
4. Response time on Hard Alpha-Beta is well under 100ms.
5. Session scoreboard and game controller transitions function accurately.
"""

import time
import random
import pytest

from game.board import (
    create_board,
    make_move,
    check_winner,
    is_terminal,
    get_legal_moves,
    EMPTY,
    PLAYER_X,
    PLAYER_O,
)
from ai.minimax import minimax_search
from ai.alphabeta import alphabeta_search
from ai.agent import (
    select_agent_move,
    get_hint_move,
    DIFFICULTY_HARD,
    DIFFICULTY_EASY,
)
from game.controller import GameController


def test_alphabeta_matches_minimax_values():
    """Verify that Alpha-Beta search yields identical evaluation values to Minimax."""
    # Test on various board states:
    test_boards = [
        # Empty board
        create_board(),
        # 1-move board: Center occupied
        (
            EMPTY, EMPTY, EMPTY,
            EMPTY, PLAYER_X, EMPTY,
            EMPTY, EMPTY, EMPTY,
        ),
        # 2-move board: Center and corner
        (
            PLAYER_O, EMPTY, EMPTY,
            EMPTY, PLAYER_X, EMPTY,
            EMPTY, EMPTY, EMPTY,
        ),
        # Mid-game board
        (
            PLAYER_X, PLAYER_O, EMPTY,
            EMPTY, PLAYER_X, EMPTY,
            PLAYER_O, EMPTY, EMPTY,
        ),
        # Imminent win scenario
        (
            PLAYER_X, PLAYER_X, EMPTY,
            PLAYER_O, PLAYER_O, EMPTY,
            EMPTY, EMPTY, EMPTY,
        ),
    ]

    for board in test_boards:
        move_mm, score_mm, nodes_mm = minimax_search(board, PLAYER_X, PLAYER_O)
        move_ab, score_ab, nodes_ab = alphabeta_search(board, PLAYER_X, PLAYER_O)

        # The evaluated value guaranteed to the player must be identical!
        assert score_ab == score_mm, f"Score mismatch on board {board}: AB={score_ab}, MM={score_mm}"
        # Alpha-beta must evaluate fewer or equal nodes
        assert nodes_ab <= nodes_mm, f"Pruning failed to reduce nodes: AB={nodes_ab}, MM={nodes_mm}"


def test_pruning_node_reduction_on_empty_board():
    """Verify pruning gain from an empty board."""
    board = create_board()
    _, _, nodes_mm = minimax_search(board, PLAYER_X, PLAYER_O)
    _, _, nodes_ab = alphabeta_search(board, PLAYER_X, PLAYER_O)

    # Pruning with move ordering drastically reduces nodes from >50,000 to ~2,000 or fewer!
    assert nodes_ab < nodes_mm
    saving_pct = ((nodes_mm - nodes_ab) / nodes_mm) * 100.0
    print(f"\n[Empty Board Search] Plain Minimax: {nodes_mm} nodes, Alpha-Beta: {nodes_ab} nodes. Reduction: {saving_pct:.2f}%")
    assert saving_pct > 80.0  # More than 80% search tree reduction


def test_hard_agent_unbeatable_as_first_player():
    """Simulate 50 games where Hard agent plays first (X) against random human moves."""
    random.seed(42)
    games_count = 50
    agent_wins = 0
    draws = 0
    human_wins = 0

    for _ in range(games_count):
        board = create_board()
        current = PLAYER_X

        while not is_terminal(board):
            if current == PLAYER_X:
                # Agent move
                decision = select_agent_move(
                    board,
                    agent_player=PLAYER_X,
                    human_player=PLAYER_O,
                    difficulty=DIFFICULTY_HARD,
                    use_pruning=True,
                )
                assert decision.move is not None
                board = make_move(board, decision.move, PLAYER_X)
                current = PLAYER_O
            else:
                # Random human move
                moves = get_legal_moves(board)
                chosen = random.choice(moves)
                board = make_move(board, chosen, PLAYER_O)
                current = PLAYER_X

        winner, _ = check_winner(board)
        if winner == PLAYER_X:
            agent_wins += 1
        elif winner == PLAYER_O:
            human_wins += 1
        else:
            draws += 1

    assert human_wins == 0, f"Hard Agent lost {human_wins} games as X!"
    assert agent_wins + draws == games_count


def test_hard_agent_unbeatable_as_second_player():
    """Simulate 50 games where Hard agent plays second (O) against random human moves."""
    random.seed(123)
    games_count = 50
    agent_wins = 0
    draws = 0
    human_wins = 0

    for _ in range(games_count):
        board = create_board()
        current = PLAYER_X

        while not is_terminal(board):
            if current == PLAYER_X:
                # Random human move
                moves = get_legal_moves(board)
                chosen = random.choice(moves)
                board = make_move(board, chosen, PLAYER_X)
                current = PLAYER_O
            else:
                # Agent move (O)
                decision = select_agent_move(
                    board,
                    agent_player=PLAYER_O,
                    human_player=PLAYER_X,
                    difficulty=DIFFICULTY_HARD,
                    use_pruning=True,
                )
                assert decision.move is not None
                board = make_move(board, decision.move, PLAYER_O)
                current = PLAYER_X

        winner, _ = check_winner(board)
        if winner == PLAYER_O:
            agent_wins += 1
        elif winner == PLAYER_X:
            human_wins += 1
        else:
            draws += 1

    assert human_wins == 0, f"Hard Agent lost {human_wins} games as O!"
    assert agent_wins + draws == games_count


def test_hard_vs_hard_always_draws():
    """When two optimal Hard agents play each other, the result must always be a draw."""
    board = create_board()
    current = PLAYER_X

    while not is_terminal(board):
        if current == PLAYER_X:
            decision = select_agent_move(board, PLAYER_X, PLAYER_O, DIFFICULTY_HARD, True)
            board = make_move(board, decision.move, PLAYER_X)
            current = PLAYER_O
        else:
            decision = select_agent_move(board, PLAYER_O, PLAYER_X, DIFFICULTY_HARD, True)
            board = make_move(board, decision.move, PLAYER_O)
            current = PLAYER_X

    winner, _ = check_winner(board)
    assert winner is None
    assert is_terminal(board)


def test_agent_speed_under_100ms():
    """Verify that Hard Alpha-Beta moves take less than 100ms."""
    board = create_board()
    # Test first move
    start = time.perf_counter()
    decision = select_agent_move(board, PLAYER_X, PLAYER_O, DIFFICULTY_HARD, use_pruning=True)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    print(f"\n[Hard Alpha-Beta Time] First move took: {elapsed_ms:.2f} ms")
    assert elapsed_ms < 100.0, f"Move took {elapsed_ms:.2f}ms which exceeds 100ms requirement"


def test_controller_gameplay_flow():
    """Verify GameController handles state changes, score keeping, and invalid moves."""
    ctrl = GameController(human_player=PLAYER_X, difficulty=DIFFICULTY_HARD, use_pruning=True)
    assert ctrl.current_turn == PLAYER_X
    assert not ctrl.game_over
    assert ctrl.scores == {"player": 0, "agent": 0, "draws": 0}

    # Human plays center (4)
    res = ctrl.play_human_move(4)
    assert res is True
    assert ctrl.board[4] == PLAYER_X
    assert ctrl.current_turn == PLAYER_O

    # Agent plays reply
    agent_dec = ctrl.play_agent_move()
    assert agent_dec is not None
    assert agent_dec.move != 4
    assert ctrl.current_turn == PLAYER_X

    # Repeated move on occupied cell should be rejected
    assert ctrl.play_human_move(4) is False


def test_random_moves_agent_difficulty():
    """Verify that Easy / Random Moves returns a legal move and single node evaluation."""
    board = create_board()
    legal_moves = get_legal_moves(board)
    decision = select_agent_move(
        board,
        agent_player=PLAYER_X,
        human_player=PLAYER_O,
        difficulty=DIFFICULTY_EASY,
    )
    assert decision.move in legal_moves
    assert decision.nodes_evaluated == 1
    assert decision.algorithm_name == "Random Selection"

