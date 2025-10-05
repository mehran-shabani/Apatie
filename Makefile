.PHONY: help up down build restart logs shell migrate makemigrations createsuperuser test lint fmt clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

build: ## Build Docker images
	docker-compose build

restart: down up ## Restart all services

logs: ## Show logs
	docker-compose logs -f

shell: ## Open Django shell
	docker-compose exec web python manage.py shell

migrate: ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose exec web python manage.py makemigrations

createsuperuser: ## Create a superuser
	docker-compose exec web python manage.py createsuperuser

test: ## Run tests
	docker-compose exec web pytest

test-cov: ## Run tests with coverage
	docker-compose exec web pytest --cov=apps --cov-report=html --cov-report=term

lint: ## Run linting
	docker-compose exec web flake8 apps config
	docker-compose exec web pylint apps config

fmt: ## Format code
	docker-compose exec web black apps config
	docker-compose exec web isort apps config

clean: ## Clean up containers and volumes
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

collectstatic: ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

dbshell: ## Open database shell
	docker-compose exec db psql -U apatye -d apatye

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

celery-status: ## Check Celery status
	docker-compose exec celery celery -A config inspect active

flower: ## Start Flower (Celery monitoring)
	docker-compose exec celery celery -A config flower --port=5555
