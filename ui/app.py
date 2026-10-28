"""
Material Design 3 User Interface for Tic Tac Toe AI (FR-01 to FR-14).

Built with Flet, providing a desktop UI featuring:
- Interactive 3x3 board with ripple effects and high-contrast typography
- Dynamic light/dark theme switching (FR-14)
- Session scoreboard (FR-11)
- Alpha-beta pruning toggle and difficulty selector (FR-08, FR-09)
- Search performance telemetry (nodes visited, runtime in ms) (FR-10)
- Optimal move hint assistant (FR-12)
- Minimax cell evaluation value overlay (FR-13)
- Winning line visualization and game-over announcement dialog (FR-05)
- In-depth AISC Viva & Algorithm theory dialog
"""

import time
from typing import Optional, List, Dict
import flet as ft

from game.board import EMPTY, PLAYER_X, PLAYER_O
from game.controller import GameController
from ai.agent import DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD


def build_app(page: ft.Page) -> None:
    """Initialize and assemble the Material Design 3 interface."""
    page.title = "Tic Tac Toe AI · AISC Project (Minimax & Alpha-Beta)"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.padding = 16
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Initialize Game Controller
    controller = GameController(
        human_player=PLAYER_X,
        difficulty=DIFFICULTY_HARD,
        use_pruning=True,
    )

    # -------------------------------------------------------------
    # Visual Theme Helpers
    # -------------------------------------------------------------
    def is_dark() -> bool:
        return page.theme_mode == ft.ThemeMode.DARK

    # -------------------------------------------------------------
    # Controls References
    # -------------------------------------------------------------
    theme_icon_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if is_dark() else ft.Icons.DARK_MODE,
        tooltip="Toggle Light/Dark Theme (FR-14)",
    )

    # Scoreboard Chips
    human_score_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)
    agent_score_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)
    draws_score_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)

    # Status Banner
    status_text = ft.Text(
        "Your Turn (Playing as X)",
        size=16,
        weight=ft.FontWeight.W_600,
        color=ft.Colors.PRIMARY,
    )
    status_icon = ft.Icon(ft.Icons.PERSON, color=ft.Colors.PRIMARY, size=20)

    # Stats Telemetry Card
    algo_name_text = ft.Text(
        "Alpha-Beta Pruning (Full Depth)",
        size=13,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY,
    )
    nodes_count_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD)
    time_taken_text = ft.Text("0.0 ms", size=18, weight=ft.FontWeight.BOLD)
    savings_badge_text = ft.Text("Baseline: 549,946 nodes", size=11, color=ft.Colors.OUTLINE)

    # Side Selection
    side_segmented_btn = ft.SegmentedButton(
        segments=[
            ft.Segment(value=PLAYER_X, label=ft.Text("Play as X (First)")),
            ft.Segment(value=PLAYER_O, label=ft.Text("Play as O (Second)")),
        ],
        selected=[PLAYER_X],
        allow_multiple_selection=False,
    )

    # Difficulty Dropdown
    difficulty_dropdown = ft.Dropdown(
        label="Difficulty Level (FR-08)",
        value=DIFFICULTY_HARD,
        options=[
            ft.DropdownOption(DIFFICULTY_EASY, text="Easy (Random Moves)"),
            ft.DropdownOption(DIFFICULTY_MEDIUM, text="Medium (Depth 2 Heuristic)"),
            ft.DropdownOption(DIFFICULTY_HARD, text="Hard (Full Search · Unbeatable)"),
        ],
        width=260,
    )

    # Switches
    pruning_switch = ft.Switch(
        label="Alpha-Beta Pruning (FR-09)",
        value=True,
        tooltip="Toggle between Plain Minimax and Alpha-Beta Pruning",
    )
    eval_overlay_switch = ft.Switch(
        label="Show Cell Minimax Values (FR-13)",
        value=False,
        tooltip="Display real-time evaluation scores on empty cells",
    )

    # Game Over Dialog
    game_over_title = ft.Text("", size=22, weight=ft.FontWeight.BOLD)
    game_over_desc = ft.Text("", size=15)
    game_over_icon = ft.Icon(ft.Icons.EMOJI_EVENTS, size=44, color=ft.Colors.AMBER)
    
    def close_dialog(e=None):
        game_over_dialog.open = False
        page.update()

    def play_again_action(e=None):
        close_dialog()
        start_new_game_action()

    game_over_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([game_over_icon, game_over_title], spacing=10),
        content=ft.Container(
            content=game_over_desc,
            padding=10,
            width=320,
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dialog),
            ft.FilledButton("Play Again", icon=ft.Icons.REPLAY, on_click=play_again_action),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(game_over_dialog)

    # Viva / Theory Dialog
    viva_dialog = ft.AlertDialog(
        modal=False,
        title=ft.Row([
            ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.PRIMARY, size=28),
            ft.Text("AISC Project Theory & PEAS", size=18, weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Artificial Intelligence & Soft Computing (AISC)", weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                    ft.Divider(),
                    ft.Text("1. PEAS Formalization:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Performance: Never lose, maximize win speed (10 - depth), delay loss (depth - 10)."),
                    ft.Text("• Environment: 3x3 board, 2 players, deterministic, discrete, fully observable."),
                    ft.Text("• Actuators: Place mark ('X' or 'O') on valid empty cell."),
                    ft.Text("• Sensors: Read 9 board cell states and current turn."),
                    ft.Divider(),
                    ft.Text("2. State Space & Search Complexity:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Reachable legal states: 5,478 positions"),
                    ft.Text("• Total possible games: 255,168 games"),
                    ft.Text("• Full game tree size: 549,946 nodes"),
                    ft.Divider(),
                    ft.Text("3. Minimax vs Alpha-Beta Pruning:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Plain Minimax evaluates all 549,946 nodes from empty board."),
                    ft.Text("• Alpha-Beta with center-corner-edge move ordering reduces search to ~7,865 nodes (98.6% pruning reduction!)"),
                    ft.Text("• Both algorithms return identical optimal values, proving admissibility."),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=8,
            ),
            width=380,
            height=420,
        ),
        actions=[
            ft.FilledButton("Got It", on_click=lambda e: (setattr(viva_dialog, 'open', False), page.update())),
        ],
    )
    page.overlay.append(viva_dialog)

    # -------------------------------------------------------------
    # 3x3 Grid Board Setup
    # -------------------------------------------------------------
    cell_containers: List[ft.Container] = []
    cell_mark_texts: List[ft.Text] = []
    cell_eval_badges: List[ft.Container] = []

    def make_cell(index: int) -> ft.Container:
        mark_text = ft.Text("", size=46, weight=ft.FontWeight.BOLD)
        cell_mark_texts.append(mark_text)

        eval_badge = ft.Container(
            content=ft.Text("", size=11, weight=ft.FontWeight.BOLD),
            visible=False,
            padding=ft.Padding(4, 2, 4, 2),
            border_radius=ft.BorderRadius.all(6),
        )
        cell_eval_badges.append(eval_badge)

        content_stack = ft.Stack(
            [
                ft.Container(
                    content=mark_text,
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
                ft.Container(
                    content=eval_badge,
                    alignment=ft.Alignment(1, -1),
                    padding=6,
                ),
            ],
            expand=True,
        )

        container = ft.Container(
            content=content_stack,
            width=100,
            height=100,
            border_radius=ft.BorderRadius.all(16),
            alignment=ft.Alignment(0, 0),
            ink=True,
            on_click=lambda e, idx=index: on_cell_clicked(idx),
            border=ft.Border.all(1.5, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH if is_dark() else ft.Colors.SURFACE_CONTAINER_LOW,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        cell_containers.append(container)
        return container

    # Build the 3x3 grid rows
    grid_rows = []
    for r in range(3):
        row_cells = []
        for c in range(3):
            idx = r * 3 + c
            row_cells.append(make_cell(idx))
        grid_rows.append(ft.Row(row_cells, spacing=10, alignment=ft.MainAxisAlignment.CENTER))

    board_widget = ft.Container(
        content=ft.Column(grid_rows, spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        alignment=ft.Alignment(0, 0),
    )

    # -------------------------------------------------------------
    # State Synchronization & UI Refresh
    # -------------------------------------------------------------
    def refresh_ui() -> None:
        # Refresh theme icon
        theme_icon_btn.icon = ft.Icons.LIGHT_MODE if is_dark() else ft.Icons.DARK_MODE

        # Refresh Scoreboard
        human_score_text.value = str(controller.scores["player"])
        agent_score_text.value = str(controller.scores["agent"])
        draws_score_text.value = str(controller.scores["draws"])

        # Side choice enabled only on fresh board
        is_empty_board = all(c == EMPTY for c in controller.board)
        side_segmented_btn.disabled = not is_empty_board
        side_segmented_btn.selected = [controller.human_player]

        # Refresh board cells
        for i in range(9):
            mark = controller.board[i]
            cell_container = cell_containers[i]
            mark_text = cell_mark_texts[i]
            eval_badge = cell_eval_badges[i]

            # Mark typography & color
            mark_text.value = mark if mark != EMPTY else ""
            if mark == PLAYER_X:
                mark_text.color = ft.Colors.BLUE_400 if is_dark() else ft.Colors.BLUE_700
            elif mark == PLAYER_O:
                mark_text.color = ft.Colors.PINK_400 if is_dark() else ft.Colors.PINK_700

            # Cell borders & styling
            is_winning_cell = controller.winning_line and i in controller.winning_line
            is_hint_cell = controller.hint_cell == i

            if is_winning_cell:
                cell_container.border = ft.Border.all(3.0, ft.Colors.GREEN_ACCENT_400)
                cell_container.bgcolor = (
                    ft.Colors.with_opacity(0.25, ft.Colors.GREEN)
                    if is_dark()
                    else ft.Colors.with_opacity(0.2, ft.Colors.GREEN_300)
                )
            elif is_hint_cell:
                cell_container.border = ft.Border.all(3.0, ft.Colors.AMBER_400)
                cell_container.bgcolor = (
                    ft.Colors.with_opacity(0.2, ft.Colors.AMBER)
                    if is_dark()
                    else ft.Colors.with_opacity(0.2, ft.Colors.AMBER_200)
                )
            else:
                cell_container.border = ft.Border.all(
                    1.5,
                    ft.Colors.OUTLINE_VARIANT if is_dark() else ft.Colors.OUTLINE,
                )
                cell_container.bgcolor = (
                    ft.Colors.SURFACE_CONTAINER_HIGH if is_dark() else ft.Colors.SURFACE_CONTAINER_LOW
                )

            # Cell Minimax Value overlay (FR-13)
            if controller.show_evaluations and mark == EMPTY and i in controller.cell_evaluations:
                score = controller.cell_evaluations[i]
                eval_badge.visible = True
                badge_text_ctrl: ft.Text = eval_badge.content  # type: ignore
                badge_text_ctrl.value = f"{score:+d}" if score != 0 else "0"
                if score > 0:
                    eval_badge.bgcolor = ft.Colors.GREEN_900 if is_dark() else ft.Colors.GREEN_100
                    badge_text_ctrl.color = ft.Colors.GREEN_ACCENT if is_dark() else ft.Colors.GREEN_800
                elif score < 0:
                    eval_badge.bgcolor = ft.Colors.RED_900 if is_dark() else ft.Colors.RED_100
                    badge_text_ctrl.color = ft.Colors.RED_ACCENT if is_dark() else ft.Colors.RED_800
                else:
                    eval_badge.bgcolor = ft.Colors.GREY_800 if is_dark() else ft.Colors.GREY_300
                    badge_text_ctrl.color = ft.Colors.GREY_300 if is_dark() else ft.Colors.GREY_800
            elif is_hint_cell:
                eval_badge.visible = True
                badge_text_ctrl = eval_badge.content  # type: ignore
                badge_text_ctrl.value = "BEST"
                eval_badge.bgcolor = ft.Colors.AMBER_900 if is_dark() else ft.Colors.AMBER_200
                badge_text_ctrl.color = ft.Colors.AMBER_ACCENT if is_dark() else ft.Colors.AMBER_900
            else:
                eval_badge.visible = False

        # Status Banner
        if controller.game_over:
            if controller.winner == controller.human_player:
                status_text.value = "Victory! You defeated the AI agent! 🎉"
                status_text.color = ft.Colors.GREEN_400 if is_dark() else ft.Colors.GREEN_700
                status_icon.name = ft.Icons.EMOJI_EVENTS
                status_icon.color = ft.Colors.GREEN_400 if is_dark() else ft.Colors.GREEN_700
            elif controller.winner == controller.agent_player:
                status_text.value = "Agent Won! Hard mode is mathematically unbeatable."
                status_text.color = ft.Colors.RED_400 if is_dark() else ft.Colors.RED_700
                status_icon.name = ft.Icons.SMART_TOY
                status_icon.color = ft.Colors.RED_400 if is_dark() else ft.Colors.RED_700
            else:
                status_text.value = "Game Drawn! Optimal play results in a draw 🤝"
                status_text.color = ft.Colors.AMBER_400 if is_dark() else ft.Colors.AMBER_700
                status_icon.name = ft.Icons.HANDSHAKE
                status_icon.color = ft.Colors.AMBER_400 if is_dark() else ft.Colors.AMBER_700
        elif controller.current_turn == controller.agent_player:
            status_text.value = "Agent is thinking... 🤖"
            status_text.color = ft.Colors.PURPLE_300 if is_dark() else ft.Colors.PURPLE_700
            status_icon.name = ft.Icons.HOURGLASS_TOP
            status_icon.color = ft.Colors.PURPLE_300 if is_dark() else ft.Colors.PURPLE_700
        else:
            status_text.value = f"Your Turn (Playing as {controller.human_player}) ✨"
            status_text.color = ft.Colors.PRIMARY
            status_icon.name = ft.Icons.PERSON
            status_icon.color = ft.Colors.PRIMARY

        # Telemetry Stats Card
        if controller.last_decision is not None:
            dec = controller.last_decision
            algo_name_text.value = dec.algorithm_name
            nodes_count_text.value = f"{dec.nodes_evaluated:,}"
            time_taken_text.value = f"{dec.time_taken_ms:.1f} ms"

            if "Alpha-Beta" in dec.algorithm_name:
                savings_badge_text.value = f"Reduced from full-tree baseline by pruning!"
            elif "Minimax" in dec.algorithm_name:
                savings_badge_text.value = "Unpruned tree traversal (Plain Minimax)"
            else:
                savings_badge_text.value = "Fast heuristic selection"

        page.update()

    # -------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------
    def on_cell_clicked(index: int) -> None:
        """Handle human player tapping on a board cell."""
        if controller.game_over or controller.current_turn != controller.human_player:
            return
        if controller.board[index] != EMPTY:
            return

        # Play human move
        applied = controller.play_human_move(index)
        if not applied:
            return

        refresh_ui()

        # If move ended game, announce result
        if controller.game_over:
            trigger_game_over_dialog()
            return

        # Trigger AI move
        def execute_agent_turn():
            time.sleep(0.05)  # Subtle pause for visual feedback
            controller.play_agent_move()
            refresh_ui()
            if controller.game_over:
                trigger_game_over_dialog()

        # In modern Flet, we can run agent move or async callback
        execute_agent_turn()

    def trigger_game_over_dialog() -> None:
        """Show victory, loss, or draw dialog."""
        if controller.winner == controller.human_player:
            game_over_title.value = "You Won! 🎉"
            game_over_desc.value = "Incredible! You found a winning path against the agent."
            game_over_icon.name = ft.Icons.EMOJI_EVENTS
            game_over_icon.color = ft.Colors.GREEN
        elif controller.winner == controller.agent_player:
            game_over_title.value = "Agent Won! 🤖"
            game_over_desc.value = (
                "The adversarial search agent exploited an opening!\n"
                f"Evaluated {controller.last_decision.nodes_evaluated if controller.last_decision else 0:,} nodes "
                f"in {controller.last_decision.time_taken_ms:.1f} ms."
                if controller.last_decision else "Adversarial search optimal move played."
            )
            game_over_icon.name = ft.Icons.SMART_TOY
            game_over_icon.color = ft.Colors.RED_ACCENT
        else:
            game_over_title.value = "Game Drawn! 🤝"
            game_over_desc.value = (
                "Perfect play on both sides! In Tic-Tac-Toe, two optimal players "
                "always reach a draw (game theoretic value = 0)."
            )
            game_over_icon.name = ft.Icons.HANDSHAKE
            game_over_icon.color = ft.Colors.AMBER

        game_over_dialog.open = True
        page.update()

    def start_new_game_action(e=None) -> None:
        """Restart board for a new game session."""
        selected_side = side_segmented_btn.selected[0] if side_segmented_btn.selected else PLAYER_X
        controller.start_new_game(
            human_player=selected_side,
            difficulty=difficulty_dropdown.value or DIFFICULTY_HARD,
            use_pruning=pruning_switch.value,
        )
        refresh_ui()

    def on_side_changed(e: ft.ControlEvent) -> None:
        """User toggled between X and O."""
        if not all(c == EMPTY for c in controller.board):
            return
        selected = e.control.selected[0] if e.control.selected else PLAYER_X
        controller.start_new_game(
            human_player=selected,
            difficulty=difficulty_dropdown.value or DIFFICULTY_HARD,
            use_pruning=pruning_switch.value,
        )
        refresh_ui()

    def on_difficulty_changed(e: ft.ControlEvent) -> None:
        """User switched difficulty level."""
        controller.difficulty = e.control.value
        refresh_ui()

    def on_pruning_toggled(e: ft.ControlEvent) -> None:
        """User toggled alpha-beta pruning switch."""
        controller.use_pruning = bool(e.control.value)
        if controller.show_evaluations:
            controller.update_evaluations()
        refresh_ui()

    def on_eval_overlay_toggled(e: ft.ControlEvent) -> None:
        """User toggled cell minimax score overlays."""
        controller.set_show_evaluations(bool(e.control.value))
        refresh_ui()

    def on_hint_clicked(e=None) -> None:
        """User requested an optimal move hint."""
        if controller.game_over or controller.current_turn != controller.human_player:
            return
        controller.request_hint()
        refresh_ui()

    def toggle_theme(e=None) -> None:
        """Switch between dark and light theme."""
        page.theme_mode = ft.ThemeMode.LIGHT if is_dark() else ft.ThemeMode.DARK
        refresh_ui()

    def reset_scores_action(e=None) -> None:
        """Clear session scoreboard."""
        controller.reset_scores()
        refresh_ui()

    def open_viva_dialog(e=None) -> None:
        """Open AISC Viva and theory information modal."""
        viva_dialog.open = True
        page.update()

    # Bind control callbacks
    theme_icon_btn.on_click = toggle_theme
    side_segmented_btn.on_change = on_side_changed
    difficulty_dropdown.on_change = on_difficulty_changed
    pruning_switch.on_change = on_pruning_toggled
    eval_overlay_switch.on_change = on_eval_overlay_toggled

    # -------------------------------------------------------------
    # Page Layout Construction
    # -------------------------------------------------------------
    # AppBar
    app_bar = ft.AppBar(
        leading=ft.Icon(ft.Icons.GRID_3X3, color=ft.Colors.PRIMARY, size=28),
        title=ft.Column(
            [
                ft.Text("Tic Tac Toe AI", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("AISC Final Project · Minimax & Alpha-Beta", size=11, color=ft.Colors.OUTLINE),
            ],
            spacing=1,
        ),
        actions=[
            ft.IconButton(
                icon=ft.Icons.SCHOOL,
                tooltip="AISC Project Theory & Viva Questions",
                on_click=open_viva_dialog,
            ),
            theme_icon_btn,
        ],
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_dark() else ft.Colors.SURFACE_CONTAINER_LOW,
    )
    page.appbar = app_bar

    # Scoreboard Card
    def score_chip(label: str, text_ctrl: ft.Text, icon_name: str, color: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon_name, size=20, color=color),
                    ft.Column(
                        [
                            ft.Text(label, size=11, weight=ft.FontWeight.W_500, color=ft.Colors.OUTLINE),
                            text_ctrl,
                        ],
                        spacing=0,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 6, 12, 6),
            border_radius=ft.BorderRadius.all(12),
            bgcolor=ft.Colors.SURFACE_CONTAINER if is_dark() else ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    scoreboard_row = ft.Row(
        [
            score_chip("YOU", human_score_text, ft.Icons.PERSON, ft.Colors.BLUE_400),
            score_chip("AGENT", agent_score_text, ft.Icons.SMART_TOY, ft.Colors.PINK_400),
            score_chip("DRAWS", draws_score_text, ft.Icons.HANDSHAKE, ft.Colors.AMBER_400),
            ft.IconButton(
                icon=ft.Icons.REPLAY_CIRCLE_FILLED,
                icon_color=ft.Colors.OUTLINE,
                tooltip="Reset Scoreboard",
                on_click=reset_scores_action,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
    )

    # Status Row
    status_card = ft.Container(
        content=ft.Row(
            [status_icon, status_text],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        padding=ft.Padding(14, 8, 14, 8),
        border_radius=ft.BorderRadius.all(10),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW if is_dark() else ft.Colors.SURFACE_CONTAINER,
    )

    # Action Buttons Row
    action_buttons = ft.Row(
        [
            ft.FilledButton(
                "New Game",
                icon=ft.Icons.REFRESH,
                on_click=start_new_game_action,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            ),
            ft.OutlinedButton(
                "Get Hint",
                icon=ft.Icons.LIGHTBULB_OUTLINE,
                on_click=on_hint_clicked,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
    )

    # Telemetry Stats Card
    stats_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=18, color=ft.Colors.PRIMARY),
                            ft.Text("Search Performance Telemetry", size=13, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            algo_name_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=12),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Nodes Evaluated", size=11, color=ft.Colors.OUTLINE),
                                    nodes_count_text,
                                ],
                                spacing=2,
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                [
                                    ft.Text("Search Runtime", size=11, color=ft.Colors.OUTLINE),
                                    time_taken_text,
                                ],
                                spacing=2,
                            ),
                        ],
                    ),
                    ft.Container(height=4),
                    savings_badge_text,
                ],
                spacing=4,
            ),
            padding=14,
            width=380,
        ),
    )

    # Options Accordion / Controls
    options_column = ft.Column(
        [
            ft.Text("Game Configuration", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE),
            side_segmented_btn,
            difficulty_dropdown,
            ft.Row([pruning_switch], alignment=ft.MainAxisAlignment.START),
            ft.Row([eval_overlay_switch], alignment=ft.MainAxisAlignment.START),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Main Page assembly
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    scoreboard_row,
                    status_card,
                    board_widget,
                    action_buttons,
                    stats_card,
                    ft.Divider(height=16),
                    options_column,
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=420,
            alignment=ft.Alignment(0, 0),
        )
    )

    refresh_ui()


def main() -> None:
    """Launch the Flet application."""
    if hasattr(ft, "run"):
        ft.run(build_app)
    elif hasattr(ft, "app"):
        ft.app(target=build_app)  # type: ignore


if __name__ == "__main__":
    main()
