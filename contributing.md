# Contributing

When contributing to this repository, please first discuss the changes you wish 
to make via [issue](https://github.com/ds-wizard/dsw-sdk/issues/new), 
[email](mailto:jakubdrahosJD@gmail.com), or any other method with the owners 
of this repository before making a change. Also look if the desired change 
hasn't been 
[already reported/resolved](https://github.com/ds-wizard/dsw-sdk/issues?q=is%3Aissue). 


## Implementation

* There is a `Makefile` in the root of the project containing targets for 
  common tasks (tests, build, etc.).
* We are using type annotations ([PEP-484](https://www.python.org/dev/peps/pep-0484/)) 
  for better readability and early error detection.
* Don't forget to check your code with `mypy`, `pylint` and `flake8` (`make 
  metrics` target) .
* Targeted Python versions are currently 3.7, 3.8 and 3.9.
* The low-level API is generated via Makefile target `make generate_api` (there 
  is a script in `src/dsw_sdk/low_level_api/tools/generate.py` that reads the 
  Swagger API specification and creates a function for every endpoint + HTTP 
  combination).
* When updating any docstrings, please generate also the docs (via `make docs`). 

## Tests

* HTTP requests in tests are recorded into Betamax cassettes – these are just 
  JSON files for storing requests and corresponding responses. Therefore, no 
  real network communication is done when running tests in normal mode.
* When running tests on your machine, it is advised to set up the 
  [DSW](https://github.com/ds-wizard/dsw-deployment-example) instance locally 
  and run tests against this instance. Don't forget to disable the Betamax 
  cassettes (`--no-cassettes` pytest flag or `make tests_no_cassettes` command).
* If you modify some part of an existing code, you should always rerecord the 
  cassettes of the corresponding tests (remove the cassettes and run tests 
  with `--recreate-cassettes` pytest option or `make record_test_cassettes 
  TESTS=name_of_the_tests`).


## Creating a pull request

* This repo follows the rules of 
  [Gitflow workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). 
  There is a separate branch for every feature/issue, branching off of the 
  `develop` branch. Each of these branches is then merged back to the `develop` 
  branch. So always choose the `develop`branch as a base when creating new PR.
* We're trying to produce better commit messages with 
  [Conventional commits](https://www.conventionalcommits.org).
