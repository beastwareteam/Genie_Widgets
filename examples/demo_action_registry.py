"""Launcher for the production Action Registry window implementation.

This file remains in examples/ as an entrypoint, while the actual feature
implementation lives in src/widgetsystem/core/action_registry_window.py.
"""

from pathlib import Path
import sys

# Add src to path for launcher execution from workspace root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.core.action_registry_window import main


if __name__ == "__main__":
    main()
