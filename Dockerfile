# Use official slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN apt-get update && apt-get install -y curl && \
  curl -sSL https://install.python-poetry.org | python3 - && \
  ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Disable Poetry virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy files required for installation
COPY pyproject.toml README.md ./
COPY src/ src/

# Install all dependencies AND the project itself
RUN poetry install

# Copy the rest of the project files for completeness
COPY . .

# Run the interactive workbench as the default command
CMD ["poetry", "run", "logic-fabricator"]
