all:
	@echo "Check makefile for possible targets."

test_release:
	python setup.py sdist

release:
	python setup.py sdist upload

test_all:
	python -m unittest discover

test_public:
	python -m unittest pyfaceb.test.test_api
