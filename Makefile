all:
	@echo "Check makefile for possible targets."

release:
	python setup.py sdist upload

tests:
	python -m unittest pyfaceb.test.test_api
