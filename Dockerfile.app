FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
# We copy only the requirements files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-interaction --no-ansi


COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "sympla_integration.wsgi:application", "--bind", "0.0.0.0:8000"]