check_quality:
	@./scripts/quality.sh

make_messages:
	@./manage.py makemessages --ignore=.venv/* -l en --no-location

compile_messages:
	@./manage.py compilemessages

pre_commit:
	@./scripts/pre_commit.sh

docker_remote:
	@ ./develop/docker_remote.sh

docker_local:
	@ ./develop/docker_local.sh

docker_stop:
	@ ./develop/docker_stop.sh

release:
	@ ./scripts/release.sh
