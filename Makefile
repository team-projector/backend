flake8:
	@flake8 apps

makemessages:
	@./manage.py makemessages --ignore=.venv/* -l en


