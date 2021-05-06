FILE := src/dsw_sdk
API_SWAGGER := https://api.demo.ds-wizard.org/swagger.json


# ------------------------------ Low-level API -------------------------------

generate_api:
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" python3 src/dsw_sdk/low_level_api/tools/generate.py "${API_SWAGGER}"

# ----------------------------------- Docs -----------------------------------

docs:
	cd docs; make html

# --------------------------------- Metrics ----------------------------------

pylint:
	pylint --exit-zero "${FILE}"

mypy:
	mypy "${FILE}"

flake8:
	flake8 --statistics --show-source --exit-zero "${FILE}"

lint: pylint flake8

metrics: pylint mypy flake8

# --------------------------------- Tests ------------------------------------

tests:
	tox -p

unit_tests:
	tox -e unit_tests

integration_tests:
	tox -e integration_tests

functional_tests:
	tox -e functional_tests

record_test_cassettes:
	rm -f tests/fixtures/cassettes/*
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" pytest --recreate-cassettes tests/

doctest:
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" pytest --doctest-modules "${FILE}"

# ------------------------------- Packaging ----------------------------------

build:
	rm -rf build dist
	python -m build

release:
	twine upload dist/*


.PHONY: docs pylint mypy flake8 metrics tests unit_tests integration_tests functional_tests build
