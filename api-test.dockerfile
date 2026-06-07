FROM python:3.12-slim

LABEL description="Metemcyber Threatconnectome"
LABEL version="0.1.0"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev
RUN groupadd -r tcuser && useradd --no-log-init -r -g tcuser tcuser
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./pyproject.toml ./uv.lock /
RUN uv sync --locked --dev --project /
USER tcuser
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:80", "--root-path", "/api", "--access-logfile", "-"]
