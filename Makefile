venv : requirements.txt
	virtualenv -p python3.7 venv
	venv/bin/pip install pip-tools isort -r requirements.txt
	venv/bin/pip install -e .
