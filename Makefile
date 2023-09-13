VENV_PATH := ./venv

test: venv
	$(VENV_PATH)/bin/coverage run -m unittest discover
	$(VENV_PATH)/bin/coverage report

lint: venv
	$(VENV_PATH)/bin/mypy .
	$(VENV_PATH)/bin/flake8 .
	$(VENV_PATH)/bin/pydocstyle .

.PHONY: setup-venv
setup-venv:
	if [ ! -d "$(VENV_PATH)" ]; then \
		python3 -m venv $(VENV_PATH); \
	fi

.PHONY: venv
venv: setup-venv
	$(VENV_PATH)/bin/pip install -e .
