#!/usr/bin/env python3
"""
Vollständige Projekt-Analyse
"""

import ast
import importlib.util
import json
from pathlib import Path


def analyze_json_files() -> None:
    """Überprüfe alle JSON-Konfigurationsdateien."""
    print("\n" + "=" * 80)
    print("JSON KONFIGURATIONSDATEIEN")
    print("=" * 80)

    config_files = {
        "config/dnd.json": "DnD Konfiguration",
        "config/i18n.de.json": "Deutsche Übersetzungen",
        "config/i18n.en.json": "Englische Übersetzungen",
        "config/layouts.json": "Layouts",
        "config/menus.json": "Menüs",
        "config/panels.json": "Panels",
        "config/responsive.json": "Responsive Design",
        "config/tabs.json": "Tabs",
        "config/themes.json": "Themes",
    }

    for file_path, description in config_files.items():
        p = Path(file_path)
        if p.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    key_count = len(data)
                    print(f"✓ {file_path:<30} | {description:<25} | {key_count:3d} keys")
                elif isinstance(data, list):
                    print(f"✓ {file_path:<30} | {description:<25} | {len(data):3d} items")
                else:
                    print(f"⚠ {file_path:<30} | {description:<25} | Type: {type(data).__name__}")
            except json.JSONDecodeError as e:
                print(f"✗ {file_path:<30} | {description:<25} | JSON ERROR: {str(e)[:50]}")
        else:
            print(f"✗ {file_path:<30} | {description:<25} | FILE NOT FOUND")


def analyze_python_files() -> None:
    """Analysiere alle Python-Dateien."""
    print("\n" + "=" * 80)
    print("PYTHON DATEIEN")
    print("=" * 80)

    py_files = [
        "dnd_factory.py",
        "i18n_factory.py",
        "layout_factory.py",
        "main.py",
        "menu_factory.py",
        "panel_factory.py",
        "responsive_factory.py",
        "tabs_factory.py",
        "theme_factory.py",
        "verify_setup.py",
    ]

    for file in py_files:
        path = Path(file)
        if path.exists():
            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()
                lines = content.count("\n") + 1
                tree = ast.parse(content)

                classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                imports = len(
                    [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))],
                )

                print(
                    f"✓ {file:<25} | {lines:4d} lines | {classes} cl | {functions:2d} fn | {imports} imp",
                )
            except SyntaxError as e:
                print(f"✗ {file:<25} | SYNTAX ERROR: {str(e)[:50]}")
        else:
            print(f"✗ {file:<25} | FILE NOT FOUND")


def check_imports() -> None:
    """Überprüfe auf fehlende Imports."""
    print("\n" + "=" * 80)
    print("IMPORT DEPENDENCIES")
    print("=" * 80)

    def has_module(module_name: str) -> bool:
        return importlib.util.find_spec(module_name) is not None

    if has_module("PySide6"):
        print("✓ PySide6 installiert")
    else:
        print("✗ PySide6 NICHT installiert")

    if has_module("PySide6QtAds"):
        print("✓ PySide6QtAds installiert")
    else:
        print("✗ PySide6QtAds NICHT installiert")

    if has_module("pylint"):
        print("✓ pylint installiert")
    else:
        print("⚠ pylint nicht installiert")

    if has_module("mypy"):
        print("✓ mypy installiert")
    else:
        print("⚠ mypy nicht installiert")


def check_type_hints() -> None:
    """Überprüfe Type-Hints in den Factories."""
    print("\n" + "=" * 80)
    print("TYPE HINTS CHECK")
    print("=" * 80)

    py_files = [
        "dnd_factory.py",
        "i18n_factory.py",
        "layout_factory.py",
        "menu_factory.py",
        "panel_factory.py",
        "responsive_factory.py",
        "tabs_factory.py",
        "theme_factory.py",
    ]

    for file in py_files:
        path = Path(file)
        if path.exists():
            with open(file, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            functions_with_hints = 0
            total_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    # Prüfe ob Return-Type annotiert ist
                    if node.returns is not None:
                        functions_with_hints += 1

            percentage = (
                (functions_with_hints / total_functions * 100) if total_functions > 0 else 0
            )
            status = "✓" if percentage >= 80 else "⚠" if percentage >= 50 else "✗"
            print(
                f"{status} {file:<25} | {percentage:5.1f}% ({functions_with_hints}/{total_functions})",
            )


if __name__ == "__main__":
    analyze_json_files()
    analyze_python_files()
    check_imports()
    check_type_hints()
    print("\n" + "=" * 80 + "\n")
