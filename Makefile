all: virtualenv
virtualenv:
	virtualenv venv
	venv/bin/pip install -r requirements.txt
	echo " " ;echo "Use this to activate the virtual environment: \"source venv/bin/activate\""
clean:
	deactivate
	rm -R venv
