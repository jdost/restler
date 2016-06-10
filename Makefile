PYTHONVERSION = $(shell python --version 2>&1 | sed 's/Python //g')
PYTHONMAJOR = $(firstword $(subst ., ,${PYTHONVERSION}))
PYTHONPATH = PYTHONPATH=$(PWD)/src
INTEGRATIONPYTHONPATH = ${PYTHONPATH}:$(PWD)/etc

init:
	pip install -r requirements.txt

unittest:
	${PYTHONPATH} nosetests --rednose ./tests/test_*.py

integration:
	${INTEGRATIONPYTHONPATH} nosetests --rednose ./tests/integration/test_*.py

lint:
	flake8 --ignore=F401,E402 --max-complexity 12 src/
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
	${PYTHONPATH} python ./etc/http_server.py -t -q & echo $$! > server.PID
	-${PYTHONPATH} python ./etc/console.py
	kill `cat server.PID`
	rm server.PID

publish:
	python setup.py register
	python setup.py sdist upload --sign --identity=2073CDA5
	python setup.py bdist_wheel upload --sign --identity=2073CDA5
