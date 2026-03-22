#!/usr/bin/env python3
"""Run all code quality checks.

Performs comprehensive quality checks:
- ruff (linting and formatting)
- mypy (type checking)
- pylint (additional linting)
- bandit (security)
- pytest (tests with coverage)
"""

import subprocess
import sys
from pathlib import Path


def run_command(name: str, command: list[str], critical: bool = True) -> bool:
    """Run a command and report status.

    Args:
        name: Display name for the check
        command: Command to run as list
        critical: Whether failure should stop execution

    Returns:
        True if successful, False otherwise
    """
    print(f"Running: {name}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(command, cwd=Path(__file__).parent.parent, check=False)
        if result.returncode == 0:
            print(f"[OK] {name}")
            return True
        print(f"[FAIL] {name}")
        if critical:
            print(f"   ERROR: {name} failed (critical check)")
        return False
    except FileNotFoundError:
        print(f"[FAIL] {name} - tool not found")
        print("   Install with: pip install -e '.[dev]'")
        return False


def main() -> int:
    """Run all checks.

    Returns:
        0 if all critical checks pass, 1 otherwise
    """
    print("=" * 70)
    print("WIDGETSYSTEM - CODE QUALITY CHECKS")
    print("=" * 70)

    project_root = Path(__file__).parent.parent
    python_cmd = sys.executable
    critical_passed = True

    # 1. Ruff - Fast linting and formatting check
    if not run_command(
        "Ruff Linting",
        [python_cmd, "-m", "ruff", "check", "src", "tests", "examples"],
        critical=True,
    ):
        critical_passed = False

    if not run_command(
        "Ruff Formatting Check",
        [python_cmd, "-m", "ruff", "format", "--check", "src", "tests", "examples"],
        critical=True,
    ):
        critical_passed = False

    # 2. MyPy - Type checking
    if not run_command(
        "MyPy Type Checking",
        [python_cmd, "-m", "mypy", "src"],
        critical=True,
    ):
        critical_passed = False

    # 3. PyLint - Additional linting (non-critical)
    run_command(
        "Pylint",
        [python_cmd, "-m", "pylint", "src/widgetsystem", "--fail-under=9.0"],
        critical=False,
    )

    # 4. Bandit - Security checks (non-critical)
    if not run_command(
        "Bandit Security Check",
        [python_cmd, "-m", "bandit", "-r", "src", "-c", "pyproject.toml"],
        critical=False,
    ):
        pass  # Security warnings non-critical

    # 5. Tests with coverage (critical)
    if not run_command(
        "Pytest with Coverage",
        [
            python_cmd,
            "-m",
            "pytest",
            "tests/",
            "--cov=src/widgetsystem",
            "--cov-report=term-missing",
        ],
        critical=True,
    ):
        critical_passed = False

    # Summary
    print("\n" + "=" * 70)
    if critical_passed:
        print("[OK] ALL CRITICAL CHECKS PASSED")
        print("=" * 70)
        print("\nYour code meets all quality standards!")
        return 0
    print("[FAIL] CRITICAL CHECKS FAILED")
    print("=" * 70)
    print("\nPlease fix the critical errors above before committing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
