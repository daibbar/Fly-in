# Variables
PYTHON      = python3
PIP         = $(PYTHON) -m pip
ENTRY       = main.py
DEFAULT_MAP = maps/challenger/01_the_impossible_dream.txt
MAP         = $(DEFAULT_MAP)

all: run

install:
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(ENTRY) $(MAP)

debug:
	$(PYTHON) -m pdb $(ENTRY) $(MAP)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache