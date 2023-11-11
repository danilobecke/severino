python = $(shell which python3)
VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
MYPY = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest
PYLINT = $(VENV)/bin/pylint

all:
	$(PYTHON) source/main.py
setup:
	$(python) -m venv $(VENV)
	$(PIP) install --upgrade setuptools
	$(PIP) install -e .
	cp scripts/pre-commit .git/hooks
	chmod 777 .git/hooks/pre-commit
mypy:
	$(MYPY) source tests --config-file configs/mypy.ini
pytest:
	$(PYTEST) --cov-report term-missing:skip-covered --cov-report xml:coverage.xml --cov=source
pylint:
	$(PYLINT) source/* tests/* --rcfile=configs/.pylintrc
