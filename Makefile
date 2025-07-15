.PHONY: cov cov-html clean clean-test clean-pyc clean-build qa format test test-single help docs
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := uv run python -c "$$BROWSER_PYSCRIPT"
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

cov: ## check code coverage
	uv run pytest -n 4 --cov cardano_tx_sanitizer

cov-html: cov ## check code coverage and generate an html report
	uv run coverage html -d cov_html
	$(BROWSER) cov_html/index.html


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr cov_html/
	rm -fr .pytest_cache

test: ## runs tests
	uv run pytest -s -vv

test-single: ## runs tests with "single" markers
	uv run pytest -s -vv -m single

qa: ## runs static analyses
	uv run flake8 cardano_tx_sanitizer
	uv run black .
	uv run ruff check .

format: ## runs code style and formatter
	uv run isort .
	uv run black .

docs: ## build the documentation
	uv export --dev --without-hashes > docs/requirements.txt
	rm -r -f docs/build
	uv run sphinx-build docs/source docs/build/html
	$(BROWSER) docs/build/html/index.html

release: clean qa test format ## build dist version and release to pypi
	uv build
	uv publish

changelog: ## Update changelog
	cz ch

bump: ## Bump version according to changelog
	cz bump

create-app: ## Create app
	uv run pyinstaller --noconfirm \
    --windowed \
    --name "Cardano Transaction Sanitizer" \
    --add-data="README.md:." \
    --icon=icon.icns \
    --collect-submodules tomli \
    --collect-submodules pydantic \
    --collect-all pycardano \
    --collect-all typeguard \
    --copy-metadata blockfrost-python \
    --collect-submodules mypyc \
    --hidden-import ddc459050edb75a05942__mypyc \
    cardano_tx_sanitizer/main.py

create-disk-image:
	mkdir -p dist/dmg
	rm -rf dist/dmg/* || true
	cp -r "dist/Cardano Transaction Sanitizer.app" dist/dmg
	test -f "dist/Cardano Transaction Sanitizer.dmg" && rm "dist/Cardano Transaction Sanitizer.dmg" || true
	create-dmg \
	  --volname "Cardano Transaction Sanitizer" \
	  --volicon "icon.icns" \
	  --window-pos 200 120 \
	  --window-size 600 300 \
	  --icon-size 100 \
	  --icon "Cardano Transaction Sanitizer.app" 175 120 \
	  --hide-extension "Cardano Transaction Sanitizer.app" \
	  --app-drop-link 425 120 \
	  "dist/Cardano Transaction Sanitizer.dmg" \
	  "dist/dmg/"