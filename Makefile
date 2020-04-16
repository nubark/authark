
clean:
	# find . -name '__pycache__' -exec rm -fr {} +
	# rm -rf ./.cache
	# rm -f .coverage
	# rm -rf .mypy_cache
	find . -name '__pycache__' -exec rm -fr {} +
	rm -rf ./.cache .mypy_cache ./schema/.mypy_cache .coverage

test:
	pytest

COVFILE ?= .coverage
#PWD = $(shell pwd)
PROJECT = authark

coverage-application:
	#mypy $(PROJECT)/application
	export COVERAGE_FILE=$(COVFILE); pytest --cov=$(PROJECT)/application \
	tests/application/ --cov-report term-missing -x -s -W \
	ignore::DeprecationWarning -o cache_dir=/tmp/authark/cache

coverage-infrastructure:
	#mypy $(PROJECT)/infrastructure
	export COVERAGE_FILE=$(COVFILE); pytest --cov=$(PROJECT)/infrastructure \
	tests/infrastructure/ --cov-report term-missing -x -s -W \
	ignore::DeprecationWarning -o cache_dir=/tmp/authark/cache

coverage: 
	export COVERAGE_FILE=$(COVFILE); pytest --cov=$(PROJECT) tests/ \
	--cov-report term-missing -x -s -vv -W ignore::DeprecationWarning \
	-o cache_dir=/tmp/authark/cache

update:
	pip-review --auto
	pip freeze > requirements.txt

serve:
	python -m $(PROJECT) serve

terminal:
	python -m $(PROJECT) terminal

PART ?= patch

version:
	bump2version $(PART) $(PROJECT)/__init__.py --tag --commit

uninstall-all:
	pip freeze | xargs pip uninstall -y

install-all:
	pip install -r requirements.txt

upgrade-all:
	pip-review --local --auto