.PHONY: help doctor test test-ui test-api backend lint check build dev audit
help:
	@echo "doctor | backend | test | test-ui | test-api | lint | check | build | dev | audit"
doctor:
	python3 scripts/doctor.py
test:
	python3 -B -m unittest discover -s tests -p 'test_*.py' -v
	python3 scripts/build_ui_climate.py --check
test-ui:
	cd prototype && npm run test:ui
lint:
	cd prototype && npm run lint -- --no-cache
check: test test-ui test-api lint
build:
	cd prototype && npm run build -- --webpack
dev:
	cd prototype && npm run dev
audit:
	cd prototype && npm audit --audit-level=high

backend:
	python3 -B scripts/setup_local_backend.py --daily
test-api:
	cd prototype && npm run test:api
