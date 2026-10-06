.PHONY: build check test eval release-check release-tag-check language-check

build:
	python3 scripts/build.py

check:
	python3 scripts/validate.py

test: check
	python3 -m unittest tests/test_tooling.py
	python3 tests/run_evaluations.py

eval:
	python3 tests/agent_eval.py $(EVAL_ARGS)

release-check: test
	python3 scripts/release_check.py

release-tag-check: release-check
	python3 scripts/release_check.py --tag

language-check:
	python3 tests/check_language_fixtures.py
