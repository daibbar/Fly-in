# Variables
PYTHON      = python3
PIP         = $(PYTHON) -m pip
ENTRY       = main.py
DEFAULT_MAP = maps/challenger/01_the_impossible_dream.txt
MAP        ?= $(DEFAULT_MAP)

.PHONY: all install run debug clean lint lint-strict

all: run

# Install project dependencies and required linters
install:
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

# Execute the simulation
run:
	$(PYTHON) $(ENTRY) $(MAP)

# Run with Python's built-in debugger (pdb)
debug:
	$(PYTHON) -m pdb $(ENTRY) $(MAP)

# Mandatory linting rule matching the subject flags exactly[cite: 1]
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# Optional strict checking recommended by the subject[cite: 1]
lint-strict:
	flake8 .
	mypy . --strict

# Clean temporary files, caches, and bytecode[cite: 1]
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache