# Use official slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN apt-get update && apt-get install -y curl && \
  curl -sSL https://install.python-poetry.org | python3 - && \
  ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Disable Poetry virtualenvs (we want everything installed globally in container)
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy only dependency files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the code
COPY src/ src/
COPY tests/ tests/

# Run tests as default command
CMD ["poetry", "run", "pytest"]

