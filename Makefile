venv : requirements.txt
	virtualenv -p python3.7 venv
	venv/bin/pip install pip-tools -r requirements.txt
