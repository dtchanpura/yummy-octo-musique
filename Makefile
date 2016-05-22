all: virtualenv
virtualenv:
	virtualenv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/python db_create.py
	venv/bin/python db_upgrade.py
	echo "Use this to activate the virtual environment: \"source venv/bin/activate\""
clean:
	#deactivate
	rm -R venv
