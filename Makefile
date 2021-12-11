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
	pylint "${FILE}"

mypy:
	mypy --install-types --non-interactive "${FILE}"

flake8:
	flake8 --statistics --show-source "${FILE}"

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
	rm -f tests/fixtures/cassettes/*"${TESTS}"*
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" pytest --recreate-cassettes -k "${TESTS}" tests/

tests_no_cassettes:
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" pytest --no-cassettes -k "${TESTS}" tests/

doctest:
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" pytest --doctest-modules "${FILE}"

# ------------------------------- Packaging ----------------------------------

build:
	rm -rf build dist
	python -m build

release:
	twine upload dist/*


.PHONY: docs pylint mypy flake8 metrics tests unit_tests integration_tests functional_tests build
