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

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt update \
    && apt install -y gcc \
                      binutils \
                      gettext \
                      nginx \
#    && chown -R www-data:www-data /var/lib/nginx \
    && pip install poetry \
    && poetry config settings.virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && apt remove --purge -y gcc binutils \
    && apt autoremove -y

COPY . .

RUN export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && cp deploy/nginx/* /etc/nginx

ENV DJANGO_ENV=production

ENTRYPOINT ["/bin/bash"]
CMD ["deploy/server/run.sh"]
