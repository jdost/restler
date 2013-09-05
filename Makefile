init:
	pip install -r requirements.txt

unittest:
	nosetests --with-color ./tests/test_*.py

lint:
	flake8 ./src/*.py
	flake8 ./tests/*.py

test: lint unittest

clean:
	rm -f ./src/*.pyc
	rm -f ./tests/*.pyc
	rm -f ./etc/*.pyc

test_server:
	python ./etc/http_server.py
