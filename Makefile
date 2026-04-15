PYTHON := python3
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate

bootstrap:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -e ".[dev]"

setup: bootstrap
	$(ACTIVATE) && pre-commit install

run:
	$(ACTIVATE) && python -m pytimeslice.interface.cli --help

test:
	$(ACTIVATE) && pytest

lint:
	$(ACTIVATE) && ruff check .

format:
	$(ACTIVATE) && black .

typecheck:
	$(ACTIVATE) && mypy src

check:
	$(ACTIVATE) && ruff check .
	$(ACTIVATE) && mypy src
	$(ACTIVATE) && pytest

clean:
	rm -rf build dist src/*.egg-info

build:
	$(ACTIVATE) && python -m build

check-dist:
	$(ACTIVATE) && python -m twine check dist/*

publish-testpypi:
	$(ACTIVATE) && python -m twine upload --repository testpypi dist/*

release-check: check build check-dist
