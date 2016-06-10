PYTHONVERSION = $(shell python --version 2>&1 | sed 's/Python //g')
PYTHONMAJOR = $(firstword $(subst ., ,${PYTHONVERSION}))
PYTHONPATH = PYTHONPATH=$(PWD)/src
INTEGRATIONPYTHONPATH = ${PYTHONPATH}:$(PWD)/etc

ifeq "${PYTHONMAJOR}" "2"
	NOSEOPTS = --with-color
else
	NOSEOPTS =
endif

init:
	pip install -r requirements.txt

unittest:
	${PYTHONPATH} nosetests ${NOSEOPTS} ./tests/test_*.py

integration:
	${INTEGRATIONPYTHONPATH} nosetests ${NOSEOPTS} ./tests/integration/test_*.py

lint:
	flake8 --ignore=F401 --max-complexity 12 src/
	flake8 --ignore=F401 --max-complexity 12 tests/

test: lint unittest

test_all: lint unittest integration

clean:
	rm -f ./src/*.pyc
	rm -f ./src/*/*.pyc
	rm -f ./tests/*.pyc
	rm -f ./etc/*.pyc

test_server:
	${PYTHONPATH} python ./etc/http_server.py

shell:
	${PYTHONPATH} python

publish:
	python setup.py register
	python setup.py sdist upload --sign --identity=2073CDA5
	python setup.py bdist_wheel upload --sign --identity=2073CDA5
