ARG UV_VERSION=0.11.19

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:3.12-slim

LABEL description="Metemcyber Threatconnectome"
LABEL version="0.1.0"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev
RUN groupadd -r tcuser && useradd --no-log-init -r -g tcuser tcuser
COPY --from=uv /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./pyproject.toml ./uv.lock /
RUN uv sync --locked --no-dev --project /
COPY ./app/ /app
USER tcuser
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8080", "--access-logfile", "-"]
