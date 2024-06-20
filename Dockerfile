FROM python:3.10-alpine

WORKDIR /app

COPY . /app

RUN pip install -r requirements.py
RUN python manage.py collectstatic --no-input
RUN playwright install --with-deps chromium
