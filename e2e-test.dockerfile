FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./pyproject.toml ./uv.lock /
RUN uv sync --locked --dev --project /
RUN uv run --locked --project / playwright install
RUN for i in 1 2 3; do uv run --locked --project / playwright install-deps && exit 0; echo "playwright install-deps failed (attempt ${i}), retrying..."; done; exit 1
