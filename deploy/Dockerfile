FROM python:3.9.7-slim as base

ENV C_FORCE_ROOT=true \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # prometheus
    prometheus_multiproc_dir=/var/run/prometheus \
    # poetry:
    POETRY_VERSION=1.1.4 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PATH="$PATH:/root/.poetry/bin"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
                      gcc=4:* \
                      libc6-dev=2.* \
                      binutils=2.* \
                      gettext=0.* \
                      nginx=1.* \
                      make=4.* \
                      curl=7.* \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python \
    && poetry install --no-dev --no-ansi \
    && apt-get remove --purge -y gcc binutils curl libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf "$POETRY_CACHE_DIR"

# ---

FROM base as production

ARG APP_VERSION

RUN addgroup --system --gid 10001 app \
    && adduser --system --uid 10001 \
        --shell /sbin/false \
        --disabled-login --ingroup app \
        --no-create-home --home /app  \
        app

COPY . .

RUN export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp deploy/nginx/* /etc/nginx \
    && chmod -R 755 /app \
    && mkdir /var/run/app \
    && mkdir /var/run/nginx \
    && chown app:app /var/run/nginx \
    && chown app:app /var/run/app \
    && chown app:app /var/log/nginx \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

ENV DJANGO_ENV=production \
    APP_VERSION=$APP_VERSION

USER app

CMD ["/bin/bash", "deploy/server/backend.sh"]

# ---

FROM base as test

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
                      gcc=4:* \
                      libc6-dev=2.* \
    && poetry install --no-ansi \
    && apt-get remove --purge -y gcc libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
