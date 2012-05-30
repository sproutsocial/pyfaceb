all:
	@echo "Check makefile for possible targets."

test_release:
	python setup.py sdist

release:
	python setup.py sdist upload

tests:
	python -m unittest pyfaceb.test.test_api
