ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SRC_DIR := ${ROOT_DIR}/cobp
TESTS_DIR := ${ROOT_DIR}/tests
VENV_DIR := ${ROOT_DIR}/venv
VENV_BIN := ${VENV_DIR}/bin
PYTHON := ${VENV_BIN}/python
ENTRYPOINT := ${SRC_DIR}/__main__.py
-include .env

install:
	${PYTHON} -m pip install .

install_dev:
	${PYTHON} -m pip install .[dev]

setup:
	python3 -m venv ${VENV_DIR}
	$(MAKE) install
	$(MAKE) install_dev

run:
	PYTHONPATH="${ROOT_DIR}" PYTHONUNBUFFERED=1 streamlit run ${ENTRYPOINT}

docker_build:
	docker build -t cobp .

docker_run:
	docker run -p 80:80 cobp

test:
	PYTHONPATH="${ROOT_DIR}" PYTHONUNBUFFERED=1 ${PYTHON} -m pytest --cov=cobp ${TESTS_DIR}

format:
	${VENV_BIN}/black ${SRC_DIR} ${TESTS_DIR}
	${VENV_BIN}/isort ${SRC_DIR} ${TESTS_DIR}

lint:
	${VENV_BIN}/ruff ${SRC_DIR}
	${VENV_BIN}/mypy ${SRC_DIR}

aws_docker_build_and_push:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${AWS_ECR_URI}
	docker build -t ${AWS_ECR_URI}/cobp:latest .
	docker push ${AWS_ECR_URI}/cobp:latest