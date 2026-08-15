FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=2.4.1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Copia primeiro os arquivos de dependências para aproveitar o cache de build.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# O processo da aplicação não roda como root.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Ambiente de desenvolvimento do exercício: prepara o banco e inicia o Django.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec python manage.py runserver 0.0.0.0:8000"]
