# Creates containers
containers:
	@echo "Creating container for DataBase"
	docker-compose -f dev_env/docker-compose.yml -p oilandrope up -d --build database
	@echo "Sleep time so DataBase can start"
	@sleep 5
	@echo "Creating container for Web"
	docker-compose -f dev_env/docker-compose.yml -p oilandrope up -d --build web

# TTY console for PDB
debug:
	docker exec -ti oilandrope_web_1 python3 "manage.py" "runserver" "0.0.0.0:9000"

# Executes TTY DBShell
dbshell:
	docker exec -ti oilandrope_database_1 psql "-U" "docker" "-h" "localhost" "oilandrope"

# Creates migration
migrations:
	@echo "Creating migrations"
	docker exec oilandrope_web_1 python3 "manage.py" "makemigrations"

# Applies migrations
migrate:
	@echo "Se migran los nuevos campos"
	docker exec oilandrope_web_1 python3 "manage.py" "migrate"

# Starts a TTY shell
shell:
	docker exec -ti oilandrope_web_1 bash

# Starts TTY Shell for DjangoExtensions
shell_plus:
	docker exec -ti oilandrope_web_1 python3 "manage.py" "shell_plus"

# Starts containers
start:
	docker start oilandrope_database_1
	@echo "Sleep so DataBase can start"
	@sleep 5
	docker start oilandrope_web_1

# Restarts containers
restart:
	docker stop oilandrope_web_1
	docker stop oilandrope_database_1
	docker start oilandrope_database_1
	@echo "Sleep so DataBase can start"
	@sleep 5
	docker start oilandrope_web_1

# Restores containers
reset:
	docker rm --force oilandrope_database_1 oilandrope_web_1
	make containers

# Compiles Sass
styles:
	sass oilandrope/core/static/core/scss/oilandrope-theme.scss:oilandrope/core/static/core/css/oilandrope-theme.css

styles-watch:
	sass oilandrope/core/static/core/scss/oilandrope-theme.scss:oilandrope/core/static/core/css/oilandrope-theme.css --watch

# Execute tests
tests:
	docker exec oilandrope_web_1 pytest
