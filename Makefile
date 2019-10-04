flake8:
	@flake8 server

mypy:
	@mypy server

check_quality:
	@./scripts/quality.sh

make_messages:
	@./manage.py makemessages --ignore=.venv/* -l en --no-location

compile_messages:
	@./manage.py compilemessages
