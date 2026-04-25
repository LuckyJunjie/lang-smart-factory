.PHONY: install run run-api test clean lint help

help:
	@echo "LangFlow Factory - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run CLI with sample requirement"
	@echo "  run-api    - Start API server"
	@echo "  test       - Run tests"
	@echo "  clean      - Clean generated files"
	@echo "  lint       - Run linter"

install:
	pip install -r requirements.txt

run:
	python cli.py run --requirement "实现一个股票筛选系统，支持A股、科创板、港股的Top10筛选"

run-api:
	python api_server.py

test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov

lint:
	@echo "Linting..."
	@command -v ruff >/dev/null 2>&1 && ruff check src/ || echo "ruff not installed"

.DEFAULT_GOAL := help

start-workers:
	@echo "Starting LangFlow Workers..."
	@python workers/implementation_worker.py &
	@echo "Implementation Worker started"

worker-status:
	@curl -s http://localhost:5001/api/v1/workers/list | python -m json.tool 2>/dev/null || echo "Workers API not running"
