FROM python:3.6-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DEFAULT_TIMEOUT=100 \
  PIPENV_HIDE_EMOJIS=true \
  PIPENV_COLORBLIND=true \
  PIPENV_NOSPIN=true \
  C_FORCE_ROOT=true

WORKDIR /var/www
COPY . /var/www

RUN apt update \
    && apt install -y gcc \
                      binutils \
                      gettext \
                      nginx \
                      git \
    && chown -R www-data:www-data /var/lib/nginx \
    && pip install poetry \
    && export DJANGO_ENV=build \
    && poetry config settings.virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp docker/nginx/* /etc/nginx \
    && apt remove --purge -y git gcc binutils \
    && apt autoremove -y

CMD ["/bin/bash", "docker/server/run.sh"]
