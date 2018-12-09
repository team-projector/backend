flake8:
	@flake8 server

makemessages:
	@./manage.py makemessages --ignore=.venv/* -l en


