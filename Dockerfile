FROM python:3.6-slim

RUN mkdir -p /var/www

ENV C_FORCE_ROOT=true

COPY . /var/www
WORKDIR /var/www

RUN apt-get update \
    && apt-get install -y gcc binutils libproj-dev gettext nginx \
    && pip install pipenv \
    && pipenv install --system --deploy \
    && export DJANGO_ENV=build \
    && python manage.py collectstatic --noinput --verbosity 0 \
    && django-admin compilemessages \
    && chown -R www-data:www-data /var/lib/nginx \
    && cp deploy/nginx.conf /etc/nginx/nginx.conf \
    && cp deploy/uwsgi_params /etc/nginx/uwsgi_params

EXPOSE 8080

CMD ["/bin/bash", "deploy/run.sh"]
