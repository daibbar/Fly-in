MAP ?= maps/easy/01_linear_path.txt

install:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install rich webcolors mypy flake8

run:
	venv/bin/python main.py $(MAP)

debug:
	venv/bin/python -m pdb main.py $(MAP)

lint:
	venv/bin/flake8 *.py
	venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf venv __pycache__ .mypy_cache