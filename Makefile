all:
	@echo "Check makefile for possible targets."

release:
	python setup.py sdist upload
