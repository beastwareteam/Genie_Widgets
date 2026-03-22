# WidgetSystem Agent Configuration

**⚠️ IMPORTANT: All AI agents working on this project must read these configuration files before starting work.**

## 📚 Configuration Files Location

This project uses comprehensive guidelines for maintaining code quality and consistency. All configuration files are in the `.github/` directory:

### Primary Configuration
- **`.github/copilot-instructions.md`** - Complete project guidelines (workspace-wide)
  - Project structure and architecture
  - Code style and conventions
  - Import rules and naming
  - Build and test commands
  - Common pitfalls to avoid

### Context-Specific Guidelines
Located in `.github/instructions/` directory:

- **`factories.instructions.md`** - Factory classes (`**/factories/**/*.py`)
  - Factory structure and patterns
  - Configuration loading
  - Type hints and error handling

- **`ui-components.instructions.md`** - UI components (`**/ui/**/*.py`, `**/core/**/*.py`)
  - PySide6 widget patterns
  - Signals and slots
  - Layout management
  - Factory integration

- **`testing.instructions.md`** - Tests (`**/tests/**/*.py`)
  - Test organization
  - Factory and UI testing
  - Integration testing

- **`json-config.instructions.md`** - JSON files (`**/config/**/*.json`)
  - Configuration structure
  - Path conventions
  - Schema validation

### Quick Reference
- **`QUICK_REFERENCE.md`** - Compact overview in German

## 🎯 For AI Agents: Required Reading

**Before making ANY changes to this codebase:**

1. **Read** `.github/copilot-instructions.md` (complete guidelines)
2. **Scan** `QUICK_REFERENCE.md` (quick overview)
3. **Check** relevant instruction file in `.github/instructions/` based on file type
4. **Review** existing code patterns in `src/widgetsystem/` 
5. **Verify** with `pytest tests/` before committing

## 🔑 Key Rules Summary

### Critical Conventions
- ✅ All source code in `src/widgetsystem/` (PEP 420 src-layout)
- ✅ Absolute imports only: `from widgetsystem.module import Class`
- ✅ Type hints required on all functions/methods
- ✅ Use `Path` objects for file paths
- ✅ Factory pattern for all UI components
- ✅ Google-style docstrings on all public APIs

### What NOT to Do
- ❌ Never create Python files in project root
- ❌ Never use relative imports (`from ..module`)
- ❌ Never hardcode absolute paths
- ❌ Never skip type hints
- ❌ Never create widgets directly (use factories)

## 🏗️ Project Structure

```
WidgetSystem/
├── .github/
│   ├── copilot-instructions.md    ← READ THIS FIRST
│   └── instructions/              ← Context-specific rules
├── src/widgetsystem/              ← All source code here
│   ├── core/                      ← Main windows
│   ├── factories/                 ← Factory classes
│   └── ui/                        ← UI components
├── tests/                         ← Test suite
├── examples/                      ← Demo applications
├── config/                        ← JSON configurations
└── QUICK_REFERENCE.md            ← Quick overview
```

## 🚀 Quick Commands

```bash
# Install
pip install -e ".[dev]"

# Test
pytest tests/

# Verify setup
python tests/verify_setup.py

# Type check
mypy src/

# Lint
ruff check src/
```

## 🤝 Multi-Agent Compatibility

This configuration works with:
- ✅ GitHub Copilot (native support)
- ✅ Claude Code (reads .md instructions)
- ✅ ChatGPT Code Interpreter (can reference files)
- ✅ VS Code Copilot Chat (uses workspace context)
- ✅ Any AI assistant with file system access

## 📖 How It Works

1. **GitHub Copilot**: Automatically loads `.github/copilot-instructions.md` for all workspace operations
2. **File-specific rules**: Apply based on `applyTo` patterns in YAML frontmatter
3. **Context injection**: Guidelines are injected into AI context when working on matching files
4. **Persistent memory**: Repository memory stores project structure for future sessions

## 🔄 Updating Guidelines

When conventions change:
1. Update relevant file in `.github/` or `.github/instructions/`
2. Commit to version control
3. Changes apply immediately to all team members and AI agents

## ⚙️ Configuration Format Compatibility

Files use:
- **Markdown format**: Universal, readable by all AI systems
- **YAML frontmatter**: Structured metadata (GitHub Copilot)
- **Plain text**: Fallback compatibility
- **Repository memory**: Workspace-scoped persistent notes

## 🆘 Troubleshooting

**If guidelines are not being followed:**

1. Verify `.github/copilot-instructions.md` exists and is readable
2. Check YAML frontmatter syntax in instruction files
3. Ensure file patterns in `applyTo` match target files
4. Try referencing this file explicitly: "Read AGENT_CONFIG.md first"
5. Check repository memory: `@workspace what are the project conventions?`

## 📞 Getting Help

- Full guidelines: `.github/copilot-instructions.md`
- Quick reference: `QUICK_REFERENCE.md`
- Examples: `tests/` and `examples/` directories
- Documentation: `docs/` directory

---

**🎯 Remember**: These guidelines ensure code quality, consistency, and maintainability. Following them is not optional—they represent team agreements and best practices for this project.
