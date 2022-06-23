PROJECT_NAME ?= market
PROJECT_NAMESPACE ?= teploeodealko
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)

all:
	@echo "make devenv		- Create & setup development virtual environment"
	@echo "make devenv		- Start development server"
	@echo "make lint		- Check code with pylama"
	@echo "make postgres	- Start postgres container"
	@echo "make test		- Run tests"
	@echo "make docker		- Build a docker image"
	@echo "make upload		- Upload docker image to the registry"
	@exit 0

devenv:
	rm -rf env
	# создаем новое окружение
	python3.9 -m venv env
	# обновляем pip
	env/bin/pip install -U pip
	# устанавливаем основные + dev зависимости из extras_require (см. setup.py)
	env/bin/pip install -r requirements.txt

devserv: export POSTGRES_NAME=postgres
devserv: export POSTGRES_USER=postgres
devserv: export POSTGRES_PASSWORD=postgres
devserv:
	python manage.py makemigrations
	python manage.py migrate
	python manage.py runserver

lint:
	pylama

postgres:
	docker stop postgres || true
	docker run --rm --detach --name=postgres \
		--env POSTGRES_USER=postgres \
		--env POSTGRES_PASSWORD=postgres \
		--env POSTGRES_DB=postgres \
		--publish 5432:5432 postgres

docker:
	docker build -t $(PROJECT_NAME) .

upload: docker
	docker tag $(PROJECT_NAME) $(REGISTRY_IMAGE)
	docker push $(REGISTRY_IMAGE)

test: export POSTGRES_NAME=postgres
test: export POSTGRES_USER=postgres
test: export POSTGRES_PASSWORD=postgres
test:
	python manage.py makemigrations
	python manage.py migrate
	pytest