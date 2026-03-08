VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

.PHONY: venv install run clean

venv:
	test -d $(VENV) || python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

run: install
	$(STREAMLIT) run app.py

clean:
	rm -rf $(VENV)
