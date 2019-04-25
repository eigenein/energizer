docs: book book.toml
	mdbook build

.PHONY: venv
venv:
	@virtualenv -p python3.7 venv
	@venv/bin/pip install -e .[dev]

.PHONY: requirements.txt
requirements.txt:
	@pip-compile --no-index --no-emit-trusted-host --generate-hashes --output-file requirements.txt setup.py

.PHONY: test
test:
	@pytest
	@flake8 myiot
	@isort -rc -c myiot tests

.PHONY: tag
tag:
	@$(eval VERSION = $(shell python setup.py --version))
	@git tag -a '$(VERSION)' -m '$(VERSION)'

# TODO: push all tags.
.PHONY: publish/tag
publish/tag: tag
	@$(eval VERSION = $(shell python setup.py --version))
	@git push origin '$(VERSION)'

.PHONY: docker
docker:
	@docker build -t eigenein/my-iot .

.PHONY:
publish/docker/latest: docker
	@docker push 'eigenein/my-iot:latest'

# TODO: check the current commit is tagged.
.PHONY: publish/docker/tag
publish/docker/tag: docker
	@$(eval VERSION = $(shell python setup.py --version))
	@docker tag 'eigenein/my-iot:latest' 'eigenein/my-iot:$(VERSION)'
	@docker push 'eigenein/my-iot:$(VERSION)'

.PHONY: publish/docker
publish/docker: publish/docker/latest publish/docker/tag

.PHONY: dist
dist:
	@rm -rf dist
	@python setup.py sdist bdist_wheel

# TODO: check the current commit is tagged.
.PHONY: publish/dist
publish/dist: dist
	@twine upload --verbose dist/*

# Publish everything, use with caution.
.PHONY: publish
publish: publish/tag publish/dist publish/docker
