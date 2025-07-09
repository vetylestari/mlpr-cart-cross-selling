FROM python:3.12.7-slim-bullseye

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    PATH="/usr/local/bin:$PATH"

# Install system deps
RUN apt-get update && apt-get upgrade -y && \
    apt-get install --no-install-recommends -y curl libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
ARG POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

WORKDIR /code

# Copy pyproject files first to leverage Docker layer cache
COPY pyproject.toml poetry.lock README.md handler_fastapi.py /code/

# Create base package folder to avoid module not found
RUN mkdir -p /code/project && touch /code/project/__init__.py

# Install Python dependencies
RUN for i in 1 2 3; do poetry install --no-interaction --no-ansi --only main && break || sleep 15; done

# Copy full project after deps installed
COPY project /code/project/

# [KEY] Ensure model/data files are inside image (not volume-mounted!)
COPY project/mlpr_cart/models /code/project/mlpr_cart/models
COPY project/mlpr_cart/data /code/project/mlpr_cart/data

# Run app using uvicorn (fallback if no CMD from docker-compose)
CMD ["poetry", "run", "uvicorn", "handler_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]