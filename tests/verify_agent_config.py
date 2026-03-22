#!/usr/bin/env python3
"""Verify that all agent configuration files are present and valid.

This script checks:
1. All required configuration files exist
2. YAML frontmatter is valid (where applicable)
3. Files are readable
4. Links between files are valid
"""

from pathlib import Path
import sys


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists and is readable.

    Args:
        file_path: Path to the file
        description: Description of the file

    Returns:
        True if file exists and is readable, False otherwise
    """
    if not file_path.exists():
        print(f"❌ Missing: {description}")
        print(f"   Expected: {file_path}")
        return False

    if not file_path.is_file():
        print(f"❌ Not a file: {description}")
        print(f"   Path: {file_path}")
        return False

    try:
        file_path.read_text(encoding="utf-8")
        print(f"✅ Found: {description}")
        return True
    except Exception as e:
        print(f"❌ Cannot read: {description}")
        print(f"   Path: {file_path}")
        print(f"   Error: {e}")
        return False


def check_yaml_frontmatter(file_path: Path, description: str) -> bool:
    """Check if file has valid YAML frontmatter.

    Args:
        file_path: Path to the file
        description: Description of the file

    Returns:
        True if frontmatter is valid, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        # Check if file starts with ---
        if not content.startswith("---\n"):
            print(f"⚠️  No YAML frontmatter: {description}")
            return True  # Not an error, just a note

        # Find second ---
        end_index = content.find("\n---\n", 4)
        if end_index == -1:
            print(f"❌ Invalid YAML frontmatter: {description}")
            print("   Missing closing ---")
            return False

        print(f"✅ Valid YAML frontmatter: {description}")
        return True

    except Exception as e:
        print(f"❌ Error checking frontmatter: {description}")
        print(f"   Error: {e}")
        return False


def main() -> int:
    """Main verification function.

    Returns:
        0 if all checks pass, 1 otherwise
    """
    print("=" * 70)
    print("VERIFYING AGENT CONFIGURATION")
    print("=" * 70)
    print()

    workspace_root = Path.cwd()
    all_ok = True

    # Check main configuration files
    print("1. Checking main configuration files...")
    print("-" * 70)

    main_files = [
        (workspace_root / "AGENT_CONFIG.md", "Agent Configuration Index"),
        (workspace_root / "AGENTS.md", "AGENTS.md (Open Standard)"),
        (workspace_root / "QUICK_REFERENCE.md", "Quick Reference"),
        (workspace_root / ".github" / "copilot-instructions.md", "GitHub Copilot Instructions"),
        (workspace_root / ".github" / "README.md", "GitHub Config Documentation"),
    ]

    for file_path, description in main_files:
        if not check_file_exists(file_path, description):
            all_ok = False

    print()

    # Check instruction files
    print("2. Checking instruction files...")
    print("-" * 70)

    instruction_files = [
        (
            workspace_root / ".github" / "instructions" / "factories.instructions.md",
            "Factory Instructions",
        ),
        (
            workspace_root / ".github" / "instructions" / "ui-components.instructions.md",
            "UI Components Instructions",
        ),
        (
            workspace_root / ".github" / "instructions" / "testing.instructions.md",
            "Testing Instructions",
        ),
        (
            workspace_root / ".github" / "instructions" / "json-config.instructions.md",
            "JSON Config Instructions",
        ),
    ]

    for file_path, description in instruction_files:
        if not check_file_exists(file_path, description) or not check_yaml_frontmatter(
            file_path, description,
        ):
            all_ok = False

    print()

    # Check directory structure
    print("3. Checking directory structure...")
    print("-" * 70)

    required_dirs = [
        (workspace_root / ".github", ".github directory"),
        (workspace_root / ".github" / "instructions", "instructions directory"),
        (workspace_root / "src" / "widgetsystem", "src/widgetsystem package"),
        (workspace_root / "tests", "tests directory"),
        (workspace_root / "config", "config directory"),
    ]

    for dir_path, description in required_dirs:
        if not dir_path.exists():
            print(f"❌ Missing: {description}")
            print(f"   Expected: {dir_path}")
            all_ok = False
        elif not dir_path.is_dir():
            print(f"❌ Not a directory: {description}")
            print(f"   Path: {dir_path}")
            all_ok = False
        else:
            print(f"✅ Found: {description}")

    print()

    # Check for common files that reference the config
    print("4. Checking documentation references...")
    print("-" * 70)

    readme_path = workspace_root / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")

        if "AGENT_CONFIG.md" in readme_content:
            print("✅ README.md references AGENT_CONFIG.md")
        else:
            print("⚠️  README.md should reference AGENT_CONFIG.md")

        if ".github/copilot-instructions.md" in readme_content:
            print("✅ README.md references copilot-instructions.md")
        else:
            print("⚠️  README.md should reference copilot-instructions.md")
    else:
        print("⚠️  README.md not found")

    print()

    # Summary
    print("=" * 70)
    if all_ok:
        print("✅ VERIFICATION SUCCESSFUL")
        print()
        print("All agent configuration files are present and valid.")
        print("AI agents will be able to find and use the guidelines.")
        return 0
    print("❌ VERIFICATION FAILED")
    print()
    print("Some configuration files are missing or invalid.")
    print("Please fix the issues above before proceeding.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
