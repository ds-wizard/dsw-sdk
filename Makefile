FILE := src/dsw_sdk
API_SWAGGER := https://api.demo.ds-wizard.org/swagger.json


# ------------------------------ Low-level API -------------------------------

generate_api:
	PYTHONPATH="`pwd`/src:${PYTHONPATH}" python3 src/dsw_sdk/low_level_api/tools/generate.py ${API_SWAGGER}

# ----------------------------------- Docs -----------------------------------

docs:
	cd docs; make html

# --------------------------------- Metrics ----------------------------------

pylint:
	pylint "${FILE}"

mypy:
	mypy "${FILE}"

flake8:
	flake8 "${FILE}"

metrics:
	-pylint "${FILE}"
	-mypy "${FILE}"
	-flake8 "${FILE}"

# --------------------------------- Tests ------------------------------------

tests:
	tox -p

unit_tests:
	tox -e unit_tests

integration_tests:
	tox -e integration_tests

functional_tests:
	tox -e functional_tests

# ------------------------------- Packaging ----------------------------------

build:
	python -m build


.PHONY: docs pylint mypy flake8 metrics tests unit_tests integration_tests functional_tests build
