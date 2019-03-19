flake8:
	@flake8 server

mypy:
	@mypy server

xenon:
	@xenon --max-absolute A --max-modules A --max-average A  -e "*/migrations/*,*/tests/*,*/management/commands/*"  apps

check_quality: flake8 mypy xenon

makemessages:
	@./manage.py makemessages --ignore=.venv/* -l en

compilemessages:
	@./manage.py compilemessages
