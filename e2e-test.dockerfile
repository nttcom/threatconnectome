FROM python:3.10-bullseye
COPY ./Pipfile.lock ./Pipfile /
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN python -m pipenv sync --dev --system
RUN pipenv run playwright install
RUN pipenv run playwright install-deps
