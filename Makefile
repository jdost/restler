init:
	pip install -r requirements.txt

unittest:
	nosetests --with-color ./tests/test_*.py

lint:
	flake8 --ignore=F401 --max-complexity 12 src/
	flake8 --ignore=F401 --max-complexity 12 tests/

test: lint unittest

clean:
	rm -f ./src/*.pyc
	rm -f ./tests/*.pyc
	rm -f ./etc/*.pyc

test_server:
	python ./etc/http_server.py
