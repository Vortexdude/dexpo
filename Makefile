.PHONY: install apply destroy help

PROJECT_NAME := $(shell basename $(PWD))
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export PYTHONPATH=.
VENV_DIR := .venv
REQUIREMENTS_FILE := requirements.txt
.DEFAULT_GOAL := help
LOCAL_EXEC := /bin/bash -c

# install requirements
install:
	@$(LOCAL_EXEC) "(./bin/install ${REQUIREMENTS_FILE})"

apply: install
	@$(LOCAL_EXEC) "(./bin/run --apply)"

destroy:
	@$(LOCAL_EXEC) "(./bin/run --destroy)"

help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@echo "  apply         - Create the infra in the AWS cloud"
	@echo "  destroy       - Destroy the resources in the cloud"
	@echo "  install       - only install Dependencies"
	@echo "  help          - Show this help message."
