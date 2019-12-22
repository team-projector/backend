FROM python:3.8-slim as base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DEFAULT_TIMEOUT=100 \
  PIPENV_HIDE_EMOJIS=true \
  PIPENV_COLORBLIND=true \
  PIPENV_NOSPIN=true \
  C_FORCE_ROOT=true \
  POETRY_VERSION=1.0.0

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt update \
    && apt install -y gcc \
                      binutils \
                      gettext \
                      nginx \
                      make \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python \
    && export PATH="$PATH:$HOME/.poetry/bin" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && apt remove --purge -y gcc binutils \
    && apt autoremove -y

# ---

FROM base as production

COPY . .

RUN export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp deploy/nginx/* /etc/nginx

ENV DJANGO_ENV=production

CMD ["/bin/bash", "deploy/server/run.sh"]

# ---

FROM base as test

RUN export PATH="$PATH:$HOME/.poetry/bin" \
    && poetry install --no-interaction --no-ansi

COPY . .
