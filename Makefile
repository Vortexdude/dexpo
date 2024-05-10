PROJECT_NAME := $(shell basename $(PWD))

.PHONY: apply destroy help
LOCAL_EXEC := /bin/bash -c

apply:
	@$(LOCAL_EXEC) "(./bin/run --apply)"

destroy:
	@$(LOCAL_EXEC) "(./bin/run --destroy)"

help:
	@echo "Available targets: ${PROJECT_NAME}"
	@echo "  apply         - Create the infra in the AWS cloud"
	@echo "  destroy       - Destroy the resources in the cloud"
	@echo "  help          - Show this help message."

.DEFAULT_GOAL := help
