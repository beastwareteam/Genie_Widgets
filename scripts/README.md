# Scripts Directory

Helper scripts for development and code quality management.

## Available Scripts

### `check_quality.py`

Runs all code quality checks in sequence. This is the recommended script to run before committing code.

**Usage:**
```bash
python scripts/check_quality.py
```

**What it checks:**
1. ✅ **Ruff Linting** - Checks code against 600+ rules
2. ✅ **Ruff Formatting** - Verifies code formatting
3. ✅ **MyPy** - Type checking with strict mode
4. ⚠️ **Pylint** - Additional linting (warnings only, min score 9.0)
5. ⚠️ **Bandit** - Security scanning (warnings only)
6. ✅ **Pytest** - Tests with 80% coverage requirement

**Exit codes:**
- `0` - All critical checks passed
- `1` - One or more critical checks failed

**Critical vs Warning checks:**
- Critical (❌): Ruff, MyPy, Pytest - Must pass
- Warning (⚠️): Pylint, Bandit - Should be reviewed but not blocking

---

### `autofix.py`

Automatically fixes common code quality issues using various tools.

**Usage:**
```bash
python scripts/autofix.py
```

**What it fixes:**
1. 🔧 **pyupgrade** - Upgrades Python syntax to 3.10+
2. 🔧 **Ruff Fix** - Auto-fixes linting issues
3. 🔧 **Ruff Format** - Formats code

**Interactive:**
- Prompts for confirmation before making changes
- Modifies files in place (commit or backup first!)

**After running:**
1. Review changes: `git diff`
2. Run quality checks: `python scripts/check_quality.py`
3. Run tests: `pytest`
4. Commit: `git commit -am 'Apply auto-fixes'`

---

## Pre-Commit Hooks

For automatic quality checks on every commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

**What pre-commit does:**
- Runs on `git commit`
- Blocks commit if checks fail
- Can auto-fix issues (you'll need to stage and commit again)
- Configured in `.pre-commit-config.yaml`

---

## Individual Tool Usage

### Ruff

```bash
# Check for issues
ruff check src/ tests/ examples/

# Auto-fix issues
ruff check --fix src/ tests/ examples/

# Format code
ruff format src/ tests/ examples/

# Check formatting only
ruff format --check src/ tests/ examples/
```

### MyPy

```bash
# Type check source code
mypy src/

# Type check with detailed output
mypy src/ --verbose
```

### Pylint

```bash
# Check code quality (min score 9.0)
pylint src/widgetsystem/

# Check with detailed report
pylint src/widgetsystem/ --reports=y
```

### Bandit

```bash
# Security scan
bandit -r src/ -c pyproject.toml

# Detailed output
bandit -r src/ -c pyproject.toml -v
```

### Pytest

```bash
# Run all tests
pytest tests/

# With coverage report
pytest tests/ --cov=src/widgetsystem --cov-report=term-missing

# Parallel execution
pytest tests/ -n auto

# Specific test file
pytest tests/test_full_system.py

# With detailed output
pytest tests/ -v
```

---

## CI/CD Integration

All scripts are designed to work in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pip install -e ".[dev]"

- name: Run quality checks
  run: python scripts/check_quality.py
```

---

## Configuration Files

All tools are configured in:
- `pyproject.toml` - Main configuration (Ruff, Pytest, Bandit, Pylint, Black, isort)
- `mypy.ini` - MyPy type checking configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

---

## Troubleshooting

### Q: "Command not found" errors
A: Install dev dependencies: `pip install -e ".[dev]"`

### Q: Scripts fail with import errors
A: Install package in editable mode: `pip install -e .`

### Q: Pre-commit hooks not running
A: Install hooks: `pre-commit install`

### Q: Too many errors from Ruff
A: Run auto-fix first: `python scripts/autofix.py`

### Q: MyPy complains about missing type hints
A: Add type annotations to all functions and methods. See copilot-instructions.md for examples.

### Q: Pylint score too low
A: Focus on Ruff and MyPy first. Pylint is additional (warnings only).

### Q: Tests fail in pytest
A: Run individual test: `pytest tests/test_name.py -v`

---

## Best Practices

1. **Before committing:**
   - Run `python scripts/check_quality.py`
   - All critical checks must pass

2. **When adding new code:**
   - Add type hints to all functions
   - Write docstrings for public APIs
   - Add tests (maintain 80% coverage)

3. **When seeing errors:**
   - Try auto-fix first: `python scripts/autofix.py`
   - Fix remaining issues manually
   - Re-run quality checks

4. **For large refactorings:**
   - Run checks frequently
   - Fix issues incrementally
   - Keep tests passing

5. **Security warnings from Bandit:**
   - Review all findings
   - Use `# nosec` only with good reason and comment

---

## Additional Resources

- **Project Guidelines**: `.github/copilot-instructions.md`
- **Agent Config**: `AGENT_CONFIG.md`, `AGENTS.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Ruff Rules**: https://docs.astral.sh/ruff/rules/
- **MyPy Docs**: https://mypy.readthedocs.io/
