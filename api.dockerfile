FROM python:3.10-slim

LABEL description="Metemcyber Threatconnectome"
LABEL version="0.1.0"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev
RUN groupadd -r tcuser && useradd --no-log-init -r -g tcuser tcuser
COPY ./Pipfile.lock ./Pipfile /
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN python -m pipenv sync --system
USER tcuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
