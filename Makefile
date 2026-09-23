.PHONY: build check test

build:
	python3 scripts/build.py

check:
	python3 scripts/validate.py

test: check
	python3 tests/run_evaluations.py
