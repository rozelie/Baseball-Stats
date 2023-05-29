ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SRC_DIR := ${ROOT_DIR}/baseball_stats
TESTS_DIR := ${ROOT_DIR}/tests
VENV_BIN := ${ROOT_DIR}/venv/bin
PYTHON := ${VENV_BIN}/python
ENTRYPOINT := ${SRC_DIR}/__main__.py

install:
	${PYTHON} -m pip install .

install_dev:
	${PYTHON} -m pip install .[dev]

setup:
	python3 -m venv venv
	$(MAKE) install
	$(MAKE) install_dev

run:
	PYTHONPATH="${ROOT_DIR}" PYTHONUNBUFFERED=1 ${PYTHON} ${ENTRYPOINT}

test:
	PYTHONPATH="${ROOT_DIR}" PYTHONUNBUFFERED=1 ${PYTHON} -m pytest ${TESTS_DIR}

format:
	${VENV_BIN}/black ${SRC_DIR} ${TESTS_DIR}
	${VENV_BIN}/isort ${SRC_DIR} ${TESTS_DIR}

lint:
	${VENV_BIN}/ruff ${SRC_DIR}
	${VENV_BIN}/mypy ${SRC_DIR}