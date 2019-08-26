flake8:
	@flake8 server

mypy:
	@mypy server

check_quality: flake8 mypy

make_messages:
	@./manage.py makemessages --ignore=.venv/* -l en

compile_messages:
	@./manage.py compilemessages
