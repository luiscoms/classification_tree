
PIP = pip3
PYTHON = python3
PIPY_REPOSITORY=pypi

ifdef PY_VENV_PATH
PYTHON_ACTIVATE = . $(PY_VENV_PATH)/bin/activate
PIP = $(PYTHON_ACTIVATE) && pip
PYTHON_BIN := $(PYTHON)
PYTHON := $(PYTHON_ACTIVATE) && $(PYTHON)
ifneq ("$(wildcard $(PY_VENV_PATH)/bin/activate)","")
$(PYTHON_ACTIVATE):
else
$(PYTHON_ACTIVATE):
	virtualenv -p$(PYTHON_BIN) $(PY_VENV_PATH)
endif
endif

.PHONY: clean
clean:
	rm -rf dist/

.PHONY: install
install:
	$(PIP) install -r requirements.txt
	$(PYTHON) setup.py install

# make test PY_VENV_PATH=env
.PHONY: lint
lint: $(PYTHON_ACTIVATE) install
	# $(PYTHON_ACTIVATE) && pep8 --exclude venv
	$(PYTHON_ACTIVATE) && pep257 classification_tree tests

# make test PY_VENV_PATH=env
.PHONY: test
test: $(PYTHON_ACTIVATE) install
	$(PYTHON_ACTIVATE) && nosetests -v --with-doctest
	# $(PYTHON) -m doctest -v classification_tree/classification_tree.py
	# $(PYTHON) -m unittest discover -v tests -p "test_*.py"

# make register PIPY_REPOSITORY=pypitest
.PHONY: register
register:
	$(PYTHON) setup.py register -r ${PIPY_REPOSITORY}

# make dist PIPY_REPOSITORY=pypitest
.PHONY: dist
dist:
	$(PYTHON) setup.py sdist

# make upload PIPY_REPOSITORY=pypitest
.PHONY: upload
upload:
	$(PYTHON) setup.py sdist upload -r ${PIPY_REPOSITORY}

ifndef VERBOSE
.SILENT:
endif
