PYTHONVERSION = $(shell python --version 2>&1 | sed 's/Python //g')
PYTHONMAJOR = $(firstword $(subst ., ,${PYTHONVERSION}))
PYTHONPATH = PYTHONPATH=$(PWD)/src
INTEGRATIONPYTHONPATH = ${PYTHONPATH}:$(PWD)/etc
TEST_VERBOSITY = 1

.PHONY: init unittest integration lint test test_all clean test_server shell publish

init:
	pip install -r requirements.txt

test: lint unittest
test_all: lint unittest integration

lint:
	@echo "Linting check"
	@flake8 --ignore=F401,E402 --max-complexity 12 src/
	@flake8 --ignore=F401 --max-complexity 12 tests/

unittest:
	@echo "Unit tests"
	@${PYTHONPATH} nosetests --verbosity=${TEST_VERBOSITY} \
		--rednose ./tests/test_*.py

integration:
	@echo "Integration tests"
	@${INTEGRATIONPYTHONPATH} nosetests --verbosity=${TEST_VERBOSITY} \
		--rednose ./tests/integration/test_*.py

clean:
	@rm -vf ./src/*.pyc
	@rm -vf ./src/*/*.pyc
	@rm -vf ./src/*/*/*.pyc
	@rm -vf ./tests/*.pyc
	@rm -vf ./etc/*.pyc
	@rm -vrf build/
	@rm -vrf dist/
	@rm -vrf *.egg-info/
	@rm -vrf ./*/__pycache__/
	@rm -vrf ./src/*/__pycache__/
	@rm -vrf ./src/*/*/__pycache__/

test_server:
	${PYTHONPATH} python ./etc/http_server.py

shell:
	@${PYTHONPATH} python ./etc/http_server.py -t -q & echo $$! > server.PID
	-${PYTHONPATH} python ./etc/console.py
	@kill `cat server.PID`
	@rm server.PID

publish:
	python setup.py register
	python setup.py sdist upload --sign --identity=2073CDA5
	python setup.py bdist_wheel upload --sign --identity=2073CDA5
