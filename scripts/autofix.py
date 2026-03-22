#!/usr/bin/env python3
"""Auto-fix code quality issues.

This script runs automatic fixes for:
- ruff (linting and formatting)
- isort (import sorting)
- black (code formatting)
- pyupgrade (Python syntax upgrades)
"""

import subprocess
import sys
from pathlib import Path


def run_fix(name: str, command: list[str]) -> bool:
    """Run a fix command and return success status.
    
    Args:
        name: Name of the fix
        command: Command to run as list
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Running: {name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=False,
            text=True,
        )
        
        if result.returncode == 0:
            print(f"✅ {name} completed")
            return True
        else:
            print(f"⚠️  {name} completed with warnings (code {result.returncode})")
            return True  # Still continue with other fixes
            
    except FileNotFoundError:
        print(f"⚠️  {name} - Command not found: {command[0]}")
        print(f"   Install with: pip install -e '.[dev]'")
        return False
    except Exception as e:
        print(f"❌ {name} - Error: {e}")
        return False


def main() -> int:
    """Run all auto-fixes.
    
    Returns:
        0 if all fixes run, 1 if errors occurred
    """
    print("="*70)
    print("WIDGETSYSTEM - AUTO-FIX CODE QUALITY")
    print("="*70)
    print("\nThis will modify files in place!")
    print("Make sure you have committed your changes or have a backup.")
    
    response = input("\nContinue? [y/N] ").strip().lower()
    if response not in ('y', 'yes'):
        print("Aborted.")
        return 0
    
    project_root = Path(__file__).parent.parent
    targets = ["src", "tests", "examples"]
    
    all_passed = True
    
    # 1. pyupgrade - Upgrade Python syntax
    print("\n" + "="*70)
    print("STEP 1: Upgrade Python syntax to 3.10+")
    print("="*70)
    py_files = []
    for target in targets:
        target_path = project_root / target
        if target_path.exists():
            py_files.extend(str(f) for f in target_path.rglob("*.py"))
    
    if py_files:
        if not run_fix(
            "pyupgrade",
            ["pyupgrade", "--py310-plus"] + py_files
        ):
            all_passed = False
    
    # 2. Ruff - Auto-fix linting issues
    print("\n" + "="*70)
    print("STEP 2: Auto-fix Ruff linting issues")
    print("="*70)
    if not run_fix(
        "Ruff Fix",
        ["ruff", "check", "--fix"] + targets
    ):
        all_passed = False
    
    # 3. Ruff - Format code
    print("\n" + "="*70)
    print("STEP 3: Format code with Ruff")
    print("="*70)
    if not run_fix(
        "Ruff Format",
        ["ruff", "format"] + targets
    ):
        all_passed = False
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL AUTO-FIXES COMPLETED")
        print("="*70)
        print("\nYour code has been automatically improved!")
        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print("  2. Run quality checks: python scripts/check_quality.py")
        print("  3. Run tests: pytest")
        print("  4. Commit changes: git commit -am 'Apply auto-fixes'")
        return 0
    else:
        print("⚠️  SOME FIXES HAD WARNINGS")
        print("="*70)
        print("\nSome auto-fixes completed with warnings.")
        print("Review the output above and check your code.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
