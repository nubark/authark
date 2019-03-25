
clean:
	find . -name '__pycache__' -exec rm -fr {} +
	rm -rf ./.cache

test:
	pytest

coverage-application: 
	pytest -x --cov=authark/application tests/application/ \
	--cov-report term-missing -s

coverage-infrastructure: 
	pytest -x --cov=authark/infrastructure tests/infrastructure/ \
	--cov-report term-missing -s --cov-config .coveragerc_infra

coverage: 
	pytest -x --cov=authark tests/ --cov-report term-missing -s \
	--cov-config .coveragerc_infra

