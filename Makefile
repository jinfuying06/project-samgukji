.PHONY: validate evaluate test

validate:
	python scripts/validate_structure.py
	python scripts/check_data_boundaries.py

evaluate:
	python evals/run_eval.py evals/eval_input.json evals/eval_results.json

test:
	python -m unittest discover -s tests -p 'test_*.py'

init-private-data:
	python scripts/init_private_data.py ../tkaf-private-data
