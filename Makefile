.PHONY: deps-compile deps-install deps-update

deps-compile:
	pip-compile requirements/base.in -o requirements/base.txt
	pip-compile requirements/dev.in -o requirements/dev.txt

deps-install:
	pip install -r requirements/dev.txt

deps-update:
	pip-compile requirements/base.in -o requirements/base.txt --upgrade
	pip-compile requirements/dev.in -o requirements/dev.txt --upgrade