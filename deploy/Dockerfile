FROM python:3.8.4-slim as base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DEFAULT_TIMEOUT=100 \
  PIPENV_HIDE_EMOJIS=true \
  PIPENV_COLORBLIND=true \
  PIPENV_NOSPIN=true \
  C_FORCE_ROOT=true \
  POETRY_VERSION=1.0.9 \
  PATH="/root/.poetry/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
                      gcc=4:8.3.0-1 \
                      libc6-dev=2.28-10 \
                      binutils=2.31.1-16 \
                      gettext=0.19.8.1-9 \
                      nginx=1.14.2-2+deb10u2 \
                      make=4.2.1-1.2 \
                      git=1:2.20.1-2+deb10u3 \
                      curl=7.64.0-4+deb10u1 \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && apt-get remove --purge -y gcc binutils curl libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---

FROM base as production

ARG APP_VERSION

COPY . .

RUN export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp deploy/nginx/* /etc/nginx

ENV DJANGO_ENV=production \
    APP_VERSION=$APP_VERSION

CMD ["/bin/bash", "deploy/server/run.sh"]

# ---

FROM base as test

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
                      gcc=4:8.3.0-1 \
                      libc6-dev=2.28-10 \
    && poetry install --no-interaction --no-ansi \
    && apt-get remove --purge -y gcc libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
