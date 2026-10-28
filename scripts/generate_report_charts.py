"""
Experimental evaluation and visualization script for the AISC Project Report.

Conducts automated experiments comparing:
1. Plain Minimax vs Alpha-Beta Pruning search node counts.
2. Search execution time across various game states and depths.
3. Pruning efficiency percentage across move ordering strategies.

Generates high-resolution publication charts saved to docs/pruning_comparison.png
and outputs summary tables for inclusion in the project report and viva defense.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np

from game.board import (
    create_board,
    make_move,
    PLAYER_X,
    PLAYER_O,
    EMPTY,
)
from ai.minimax import minimax_search
from ai.alphabeta import alphabeta_search


def run_benchmark():
    print("=" * 70)
    print("AISC PROJECT BENCHMARK: Minimax vs Alpha-Beta Pruning")
    print("=" * 70)

    # Scenarios to test:
    # 1. Empty Board (Turn 1, 9 empty cells)
    # 2. Turn 2 (Human played corner (0), Agent picking move 2)
    # 3. Turn 3 (Move 0, 4 played, 7 cells open)
    # 4. Turn 4 (4 cells occupied, 5 open)
    # 5. Turn 5 (5 cells occupied, 4 open)
    scenarios = [
        ("Turn 1 (9 empty)", create_board()),
        ("Turn 2 (8 empty)", make_move(create_board(), 0, PLAYER_X)),
        ("Turn 3 (7 empty)", make_move(make_move(create_board(), 0, PLAYER_X), 4, PLAYER_O)),
        ("Turn 4 (6 empty)", make_move(make_move(make_move(create_board(), 0, PLAYER_X), 4, PLAYER_O), 1, PLAYER_X)),
        ("Turn 5 (5 empty)", make_move(make_move(make_move(make_move(create_board(), 0, PLAYER_X), 4, PLAYER_O), 1, PLAYER_X), 2, PLAYER_O)),
    ]

    labels = []
    minimax_nodes = []
    alphabeta_nodes = []
    minimax_times = []
    alphabeta_times = []
    pruning_savings = []

    for name, board in scenarios:
        print(f"\nEvaluating: {name} ...")
        # Minimax
        t0 = time.perf_counter()
        move_mm, score_mm, nodes_mm = minimax_search(board, PLAYER_O, PLAYER_X)
        t_mm = (time.perf_counter() - t0) * 1000.0

        # Alpha-Beta
        t0 = time.perf_counter()
        move_ab, score_ab, nodes_ab = alphabeta_search(board, PLAYER_O, PLAYER_X)
        t_ab = (time.perf_counter() - t0) * 1000.0

        savings = ((nodes_mm - nodes_ab) / nodes_mm) * 100.0

        assert score_mm == score_ab, f"Scores do not match: MM={score_mm}, AB={score_ab}"

        labels.append(name.split(" ")[0] + " " + name.split(" ")[1])
        minimax_nodes.append(nodes_mm)
        alphabeta_nodes.append(nodes_ab)
        minimax_times.append(t_mm)
        alphabeta_times.append(t_ab)
        pruning_savings.append(savings)

        print(f"  Plain Minimax : {nodes_mm:>8,d} nodes | {t_mm:>8.2f} ms | Score: {score_mm}")
        print(f"  Alpha-Beta    : {nodes_ab:>8,d} nodes | {t_ab:>8.2f} ms | Score: {score_ab}")
        print(f"  Pruning Gain  : {savings:>7.2f}% node reduction")

    # Generate Graphs
    os.makedirs("docs", exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(labels))
    width = 0.35

    # Chart 1: Node Count (Log Scale)
    rects1 = ax1.bar(x - width/2, minimax_nodes, width, label='Plain Minimax', color='#EF4444', alpha=0.9)
    rects2 = ax1.bar(x + width/2, alphabeta_nodes, width, label='Alpha-Beta Pruning', color='#10B981', alpha=0.9)
    ax1.set_ylabel('Nodes Evaluated (Log Scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Search Tree Size: Minimax vs Alpha-Beta', fontsize=14, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_yscale('log')
    ax1.legend(fontsize=11)
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Annotate percentage savings on bars
    for i, sav in enumerate(pruning_savings):
        ax1.annotate(
            f"-{sav:.1f}%",
            xy=(x[i] + width/2, alphabeta_nodes[i]),
            xytext=(0, 6),
            textcoords="offset points",
            ha='center', va='bottom',
            fontsize=9, fontweight='bold', color='#047857',
        )

    # Chart 2: Execution Time (ms)
    rects3 = ax2.bar(x - width/2, minimax_times, width, label='Plain Minimax', color='#F59E0B', alpha=0.9)
    rects4 = ax2.bar(x + width/2, alphabeta_times, width, label='Alpha-Beta Pruning', color='#3B82F6', alpha=0.9)
    ax2.set_ylabel('Execution Time (milliseconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Search Latency Comparison (ms)', fontsize=14, fontweight='bold', pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10)
    ax2.legend(fontsize=11)
    ax2.grid(True, ls="--", alpha=0.5)

    plt.tight_layout()
    chart_path = os.path.join("docs", "pruning_comparison.png")
    plt.savefig(chart_path, dpi=300)
    print(f"\n[OK] Chart successfully saved to: {chart_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
