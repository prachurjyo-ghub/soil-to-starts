.PHONY: help doctor workflow-check test lint check build dev audit
help:
	@echo "doctor | workflow-check | test | lint | check | build | dev | audit"
doctor:
	python3 scripts/doctor.py
workflow-check:
	python3 scripts/workflow.py check
test:
	python3 -B -m unittest discover -s tests -p 'test_*.py' -v
lint:
	cd prototype && npm run lint -- --no-cache
check: test workflow-check lint
build:
	cd prototype && npm run build -- --webpack
dev:
	cd prototype && npm run dev

audit:
	cd prototype && npm audit --audit-level=high
