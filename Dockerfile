FROM docker.io/python:alpine as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN apk update && apk add curl gcc musl-dev libffi-dev openssl-dev make g++ libxml2-dev libxslt-dev

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./
COPY ./pyproject.toml ./
RUN poetry install --no-dev

FROM python-base as production

COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY ./soil-moisture-sensor ./app
WORKDIR ./app

RUN ls $VENV_PATH/bin
RUN ls .

CMD ["python", "./app.py"]
