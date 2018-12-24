PIP := venv/bin/pip
PIP-COMPILE := venv/bin/pip-compile
PYTHON := venv/bin/python
TWINE := venv/bin/twine

.PHONY : \
	requirements.txt \
	tag \
	publish/tag \
	docker \
	publish/docker \
	dist \
	publish/dist

venv : requirements.txt
	@virtualenv -p python3.7 venv
	@$(PIP) install pip-tools isort ipython
	@$(PIP) install -r requirements.txt
	@$(PIP) install -e .

requirements.txt : setup.py
	@$(PIP-COMPILE) --no-index --no-emit-trusted-host --generate-hashes --output-file requirements.txt setup.py

tag : venv
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git tag -a '$(VERSION)' -m '$(VERSION)'

publish/tag : tag
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git push origin '$(VERSION)'

docker :
	@docker build -t eigenein/iftttie .

publish/docker : docker
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@docker tag 'eigenein/iftttie:latest' 'eigenein/iftttie:$(VERSION)'
	@docker push 'eigenein/iftttie:latest'
	@docker push 'eigenein/iftttie:$(VERSION)'

dist : venv
	@rm -rf dist
	@$(PYTHON) setup.py sdist bdist_wheel

publish/dist : dist
	@$(TWINE) upload --verbose dist/*
