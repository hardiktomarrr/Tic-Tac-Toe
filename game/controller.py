"""
Game controller linking the UI and the AI agent (FR-01 to FR-14).

Maintains game session state, turn coordination, score keeping,
and triggers AI move evaluations.
"""

from typing import Tuple, Optional, Dict, Callable
from game.board import (
    create_board,
    make_move,
    check_winner,
    is_terminal,
    is_full,
    EMPTY,
    PLAYER_X,
    PLAYER_O,
)
from ai.agent import (
    select_agent_move,
    get_hint_move,
    get_cell_minimax_values,
    AgentDecision,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
)


class GameController:
    """Coordinates gameplay between Human and AI Agent."""

    def __init__(
        self,
        human_player: str = PLAYER_X,
        difficulty: str = DIFFICULTY_HARD,
        use_pruning: bool = True,
    ) -> None:
        self.human_player: str = human_player
        self.agent_player: str = PLAYER_O if human_player == PLAYER_X else PLAYER_X
        self.difficulty: str = difficulty
        self.use_pruning: bool = use_pruning
        
        self.board: Tuple[str, ...] = create_board()
        self.current_turn: str = PLAYER_X  # X always moves first
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.is_draw: bool = False
        self.winning_line: Optional[Tuple[int, int, int]] = None
        
        self.last_decision: Optional[AgentDecision] = None
        self.hint_cell: Optional[int] = None
        self.cell_evaluations: Dict[int, int] = {}
        self.show_evaluations: bool = False
        
        # Session Scoreboard (FR-11)
        self.scores: Dict[str, int] = {
            "player": 0,
            "agent": 0,
            "draws": 0,
        }

    def start_new_game(
        self,
        human_player: Optional[str] = None,
        difficulty: Optional[str] = None,
        use_pruning: Optional[bool] = None,
    ) -> None:
        """
        Reset the board and begin a new match.
        Retains session scoreboard statistics.
        """
        if human_player is not None:
            self.human_player = human_player
            self.agent_player = PLAYER_O if human_player == PLAYER_X else PLAYER_X
        if difficulty is not None:
            self.difficulty = difficulty
        if use_pruning is not None:
            self.use_pruning = use_pruning

        self.board = create_board()
        self.current_turn = PLAYER_X
        self.game_over = False
        self.winner = None
        self.is_draw = False
        self.winning_line = None
        self.hint_cell = None
        self.cell_evaluations = {}
        
        # If human chose 'O', agent (X) moves first!
        if self.agent_player == PLAYER_X:
            self.play_agent_move()
        elif self.show_evaluations:
            self.update_evaluations()

    def play_human_move(self, index: int) -> bool:
        """
        Attempt to place the human player's mark on the board.
        
        Args:
            index: Cell index 0 to 8.
            
        Returns:
            True if move was accepted and applied, False otherwise.
        """
        if self.game_over:
            return False
        if self.current_turn != self.human_player:
            return False
        if not (0 <= index < 9) or self.board[index] != EMPTY:
            return False

        # Apply human move
        self.board = make_move(self.board, index, self.human_player)
        self.hint_cell = None
        
        # Check game state
        if self._evaluate_terminal():
            return True

        # Switch to Agent turn
        self.current_turn = self.agent_player
        return True

    def play_agent_move(self) -> Optional[AgentDecision]:
        """
        Trigger the AI agent to search and execute its move.
        
        Returns:
            AgentDecision containing stats, or None if not agent's turn.
        """
        if self.game_over or self.current_turn != self.agent_player:
            return None

        decision = select_agent_move(
            board=self.board,
            agent_player=self.agent_player,
            human_player=self.human_player,
            difficulty=self.difficulty,
            use_pruning=self.use_pruning,
        )
        self.last_decision = decision

        if decision.move is not None:
            self.board = make_move(self.board, decision.move, self.agent_player)

        # Check game state
        if not self._evaluate_terminal():
            self.current_turn = self.human_player
            if self.show_evaluations:
                self.update_evaluations()

        return decision

    def request_hint(self) -> Optional[int]:
        """
        Compute and store the optimal move for human (FR-12).
        
        Returns:
            Recommended cell index or None.
        """
        if self.game_over or self.current_turn != self.human_player:
            return None
        self.hint_cell = get_hint_move(
            self.board,
            human_player=self.human_player,
            agent_player=self.agent_player,
            use_pruning=self.use_pruning,
        )
        return self.hint_cell

    def update_evaluations(self) -> None:
        """Compute minimax scores for all currently empty cells (FR-13)."""
        if self.game_over:
            self.cell_evaluations = {}
            return
        self.cell_evaluations = get_cell_minimax_values(
            self.board,
            player_turn=self.current_turn,
            opponent=self.human_player if self.current_turn == self.agent_player else self.agent_player,
            use_pruning=self.use_pruning,
        )

    def set_show_evaluations(self, show: bool) -> None:
        """Toggle cell evaluation overlay."""
        self.show_evaluations = show
        if show:
            self.update_evaluations()
        else:
            self.cell_evaluations = {}

    def reset_scores(self) -> None:
        """Reset scoreboard to zero."""
        self.scores = {"player": 0, "agent": 0, "draws": 0}

    def _evaluate_terminal(self) -> bool:
        """
        Check if current board is terminal, set state flags, and update scores.
        
        Returns:
            True if terminal, False otherwise.
        """
        winner, line = check_winner(self.board)
        if winner is not None:
            self.game_over = True
            self.winner = winner
            self.winning_line = line
            self.cell_evaluations = {}
            if winner == self.human_player:
                self.scores["player"] += 1
            else:
                self.scores["agent"] += 1
            return True
        elif is_full(self.board):
            self.game_over = True
            self.is_draw = True
            self.cell_evaluations = {}
            self.scores["draws"] += 1
            return True
        return False
