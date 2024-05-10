.PHONY: install apply destroy help

PROJECT_NAME := $(shell basename $(PWD))
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export PYTHONPATH=.
VENV_DIR := .venv
REQUIREMENTS_FILE := requirements.txt
.DEFAULT_GOAL := help
LOCAL_EXEC := /bin/bash -c

# install requirements
install: $(VENV_DIR)/bin/activate
	@echo "Installing Python dependencies..."
	@$(VENV_DIR)/bin/pip3 install -r $(REQUIREMENTS_FILE)
	@echo "Python dependencies installed successfully."


# check the python virtual env is created or not
$(VENV_DIR)/bin/activate:
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)."

apply: install
	@$(LOCAL_EXEC) "(./bin/run --apply)"

destroy: install
	@$(LOCAL_EXEC) "(./bin/run --destroy)"

help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@echo "  apply         - Create the infra in the AWS cloud"
	@echo "  destroy       - Destroy the resources in the cloud"
	@echo "  install       - only install Dependencies"
	@echo "  help          - Show this help message."
