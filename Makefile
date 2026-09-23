.PHONY: build check test release-check

build:
	python3 scripts/build.py

check:
	python3 scripts/validate.py

test: check
	python3 tests/run_evaluations.py

release-check: test
	python3 scripts/release_check.py
