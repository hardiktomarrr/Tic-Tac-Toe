#!/usr/bin/env python3
"""
Tic Tac Toe AI Agent (Minimax + Alpha-Beta Pruning)
Submission for Artificial Intelligence and Soft Computing (AISC)

Starts the Material Design 3 desktop interface.
"""

import sys
from ui.app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame exited by user.")
        sys.exit(0)
