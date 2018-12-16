venv : requirements.txt
	@virtualenv -p python3.7 venv
	@venv/bin/pip install pip-tools isort ipython -r requirements.txt
	@venv/bin/pip install -e .

requirements.txt : setup.py
	@venv/bin/pip-compile --no-index --no-emit-trusted-host --generate-hashes --output-file requirements.txt setup.py
