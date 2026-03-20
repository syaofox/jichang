# AGENTS.md

## Project Overview

This is a Python CLI tool for validating OpenClash (Clash proxy) configuration files.
It checks YAML syntax, validates proxy group references, and validates rule syntax.
Also includes a Web UI editor for managing configurations.

**Entry points:**
- `validate_config.py` — CLI validator
- `api/main.py` — Web UI server

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Validate default config (configs/dns.yaml)
python validate_config.py

# Validate a specific file
python validate_config.py myconfig.yaml

# Validate with custom config directory
python validate_config.py -c /path/to/configs myconfig.yaml

# Skip checks
python validate_config.py --no-check-proxies --no-check-rules

# Start Web UI editor
python api/main.py
# Or use the startup script (auto-creates venv)
./run.sh
# Then open http://localhost:8000
```

## Commands

### Running the Tool
```bash
python validate_config.py [config_file] [-c CONFIG_DIR]
```

### Testing
```bash
# Manual test: run against sample configs
python validate_config.py
python validate_config.py dns-origin.yaml
```

### Linting (if configured)
```bash
uvx ruff check .
uvx ruff format .
```

### Type Checking
```bash
uvx mypy validate_config.py
```

## Code Style Guidelines

### General
- Python 3, single-file scripts preferred
- Use `argparse` for CLI argument parsing
- Exit with `sys.exit(0)` on success, `sys.exit(1)` on failure
- Print errors to `sys.stderr`, progress/success to `stdout`

### Imports
- Standard library first, then third-party
- Group: `argparse` → `re`, `sys`, `pathlib` → third-party (`yaml`)
- Use `from pathlib import Path` for path operations

### Naming Conventions
- Constants: `UPPER_SNAKE_CASE` (e.g., `RULE_TYPES`, `NO_RESOLVE_RULE_TYPES`)
- Functions: `snake_case`
- Variables: `snake_case`
- Classes: `PascalCase` (avoid if possible — prefer module-level functions)
- CLI flags: `snake_case` with `--kebab-case` aliases

### Formatting
- 4-space indentation
- Max line length: 88 (ruff default)
- Use implicit string concatenation where appropriate
- Blank lines: two between top-level definitions, one between functions

### Type Hints
- Add type hints for function signatures (not currently used, but recommended)
- Use `from __future__ import annotations` for forward references if needed

### Error Handling
- Use specific exception types (`yaml.YAMLError`)
- Collect all errors/warnings into lists, report at the end
- Print error messages with file:line context

### Docstrings
- Module-level: one-line summary in `"""` on first line
- Functions: Google-style docstring if complex logic

### Strings
- Use double quotes for user-facing strings
- Use single quotes for internal/technical strings
- f-strings for string formatting
- Always specify encoding when opening files: `encoding="utf-8"`

### Data Structures
- Use `dict` and `set` comprehensions where concise
- `dict.get(key, default)` for safe access
- Use `isinstance()` checks before accessing dict keys

## Project Structure

```
/mnt/github/jichang/
├── validate_config.py     # CLI validator
├── api/
│   └── main.py            # FastAPI Web UI server
├── static/
│   ├── index.html         # Web UI page
│   ├── style.css          # Styles
│   └── app.js             # Frontend logic
├── configs/               # Sample YAML configs
│   ├── dns.yaml
│   └── dns-origin.yaml
├── rule-providers/        # Rule provider files (*.list)
├── requirements.txt       # Python dependencies
├── .gitignore
└── AGENTS.md              # This file
```

## Dependency

- `pyyaml` — YAML parsing (required for both CLI and Web UI)
- `fastapi` — Web framework for Web UI
- `uvicorn` — ASGI server for FastAPI

Install via: `pip install -r requirements.txt`

## Notes

- The validator is strict about rule types and proxy references
- Logic rules (`AND`, `OR`, `NOT`, `SUB-RULE`) require parentheses in condition field
- `RULE-SET` type requires the provider to be defined in `rule-providers` section
- No-resolve flag (`no-resolve`) is supported for GEOIP, IP-CIDR, etc.
