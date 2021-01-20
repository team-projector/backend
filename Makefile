check_quality:
	@./scripts/quality.sh

make_messages:
	@./manage.py makemessages --ignore=.venv/* -l en -l ru --no-location

compile_messages:
	@./manage.py compilemessages

generate_graphql_schema:
	@./manage.py graphql_schema --schema server.gql.schema --out tests/schema.graphql

pre_commit:
	@ pre-commit

pre_commit_install:
	@ pre-commit install && pre-commit install --hook-type commit-msg

pre_commit_update:
	@ pre-commit autoupdate

docker_remote:
	@ ./develop/docker_remote.sh

docker_local:
	@ ./develop/docker_local.sh

docker_stop:
	@ ./develop/docker_stop.sh

release:
	@ ./scripts/release.sh
