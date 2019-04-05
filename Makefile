.PHONY: venv
venv:
	@virtualenv -p python3.7 venv
	@venv/bin/pip install -e .[dev]

.PHONY: requirements.txt
requirements.txt :
	@pip-compile --no-index --no-emit-trusted-host --generate-hashes --output-file requirements.txt setup.py

.PHONY: test
test:
	pytest
	flake8 iftttie

.PHONY: tag
tag:
	@$(eval VERSION = $(shell python setup.py --version))
	@git tag -a '$(VERSION)' -m '$(VERSION)'

.PHONY: publish/tag
publish/tag: tag
	@$(eval VERSION = $(shell python setup.py --version))
	@git push origin '$(VERSION)'

.PHONY: docker
docker:
	@docker build -t eigenein/iftttie .

.PHONY:
publish/docker/latest: docker
	@docker push 'eigenein/iftttie:latest'

.PHONY: publish/docker/tag
publish/docker/tag: docker
	@$(eval VERSION = $(shell python setup.py --version))
	@docker tag 'eigenein/iftttie:latest' 'eigenein/iftttie:$(VERSION)'
	@docker push 'eigenein/iftttie:$(VERSION)'

.PHONY: publish/docker
publish/docker : publish/docker/latest publish/docker/tag

.PHONY: dist
dist:
	@rm -rf dist
	@python setup.py sdist bdist_wheel

.PHONY: publish/dist
publish/dist: dist
	@twine upload --verbose dist/*
