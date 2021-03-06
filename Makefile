# NOTE: gfortran is used for compilation

NAME := e3smdiff
PY := python3
CASE1 := data/cases/SMS.T62_oQU120_ais20.MPAS_LISIO_TEST.spock_gnu.20211021_182634_4foh9f
#CASE2 := data/cases/SMS_R_Ld5.ne4_ne4.FSCM5A97.spock_gnu.eam-scm.20211021_182634_4foh9f
CASE2 := /Users/8yk/repos/github/e3smdiff/data/cases/SMS_R_Ld5.ne4_ne4.FSCM5A97.spock_gnu.eam-scm.20211021_182634_4foh9f
CASES1 := /ccs/home/grnydawn/prjcli133/e3sm_scratch/spock_cray/SMS.T62_oQU120_ais20.MPAS_LISIO_TEST.spock_cray.20211026_082541_5xjzcm
CASES2 := /ccs/home/grnydawn/prjcli133/e3sm_scratch/spock_cray/SMS_P12x2.ne4_oQU240.WCYCL1850NS.spock_cray.allactive-mach_mods.20211026_082541_5xjzcm
 
.PHONY: clean clean-test clean-pyc clean-build doc help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := ${PY} -c "$$BROWSER_PYSCRIPT"

SHAREDIR := /media/sf_VM-Shared
SHAREWORK := ${SHAREDIR}/${NAME}

help:
	@${PY} -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 ${NAME} tests

test: ## run tests quickly with the default Python
	e3smdiff ${CASE1} ${CASE2}
	#pytest ./tests -s -vv --pyargs ${NAME}

stest: ## run tests quickly with the default Python
	e3smdiff ${CASES1} ${CASES2}
	#pytest ./tests -s -vv --pyargs ${NAME}

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	#coverage run --source ${NAME} -m unittest
	coverage run --source ${NAME} pytest --pyargs ${NAME}
	coverage report -m
	#coverage html
	#$(BROWSER) htmlcov/index.html

doc: ## generate Sphinx HTML docsumentation, including API docs
	#rm -f doc/${NAME}.rst
	#rm -f doc/modules.rst
	#sphinx-apidoc -o doc/ ${NAME}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html

servedoc: doc ## compile the docss watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C doc html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	${PY} setup.py sdist
	${PY} setup.py bdist_wheel --universal
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	${PY} setup.py install

dev-install: clean ## install the package locally
	pip install -e .
	#${PY} setup.py develop
	#${PY} setup.py develop --user

sshspock:
	ssh -L localhost:8000:localhost:8000 grnydawn@spock.olcf.ornl.gov
