.PHONY: help install dev-install run clean test format lint setup

# Default target
help:
	@echo "🚀 Agentic PPT - Available commands:"
	@echo ""
	@echo "  setup      - Complete project setup (install uv, create venv, install deps)"
	@echo "  install    - Install dependencies using uv"
	@echo "  dev-install- Install development dependencies"
	@echo "  run        - Start the Streamlit application"
	@echo "  clean      - Clean up temporary files and cache"
	@echo "  test       - Run tests (when available)"
	@echo "  format     - Format code with black"
	@echo "  lint       - Run linting with flake8"
	@echo "  env        - Copy environment template"
	@echo ""

# Complete project setup
setup:
	@echo "🔧 Setting up Agentic PPT project..."
	@echo "📦 Installing uv (if not already installed)..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh || echo "uv already installed"
	@echo "🐍 Creating virtual environment and installing dependencies..."
	uv venv
	uv pip install -r requirements.txt
	@echo "📄 Setting up environment file..."
	@if [ ! -f .env ]; then cp env_template.txt .env; echo "✅ Created .env file from template"; fi
	@echo ""
	@echo "✅ Setup complete! Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make run' to start the application"

# Install dependencies
install:
	@echo "📦 Installing dependencies with pip..."
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

# Install development dependencies
dev-install:
	@echo "📦 Installing development dependencies..."
	uv venv
	uv pip install -r requirements.txt
	uv pip install pytest black flake8 mypy

# Run the application
run:
	@echo "🚀 Starting Agentic PPT application..."
	.venv/bin/python run.py

# Alternative run command using streamlit directly
run-streamlit:
	@echo "🚀 Starting with streamlit directly..."
	.venv/bin/streamlit run app.py

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Run tests (placeholder)
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v || echo "No tests found"

# Format code
format:
	@echo "🎨 Formatting code with black..."
	uv run black .

# Lint code
lint:
	@echo "🔍 Linting code with flake8..."
	uv run flake8 .

# Copy environment template
env:
	@if [ ! -f .env ]; then \
		cp env_template.txt .env; \
		echo "✅ Created .env file from template"; \
		echo "📝 Please edit .env with your API keys"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

# Show project status
status:
	@echo "📊 Project Status:"
	@echo "Python version: $(shell python --version 2>/dev/null || echo 'Not found')"
	@echo "UV version: $(shell uv --version 2>/dev/null || echo 'Not installed')"
	@echo "Virtual env: $(shell uv run python -c 'import sys; print(sys.prefix)' 2>/dev/null || echo 'Not activated')"
	@echo "Dependencies installed: $(shell uv pip list 2>/dev/null | wc -l || echo 'Unknown')"
	@echo ".env file: $(shell [ -f .env ] && echo 'Exists' || echo 'Missing')" 