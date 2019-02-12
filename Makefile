flake8:
	@flake8 server

mypy:
	@mypy server

quality: flake8 mypy

makemessages:
	@./manage.py makemessages --ignore=.venv/* -l en


