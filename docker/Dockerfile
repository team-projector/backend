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

RUN apt-get update \
    && apt-get install -y gcc binutils libproj-dev gettext nginx \
    && chown -R www-data:www-data /var/lib/nginx \
    && pip install pipenv \
    && pipenv install --system --deploy \

WORKDIR /var/www
COPY . /var/www

RUN export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp docker/nginx/* /etc/nginx

CMD ["/bin/bash", "docker/server/run.sh"]
