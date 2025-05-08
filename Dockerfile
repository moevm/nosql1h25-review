FROM python:3.11-alpine
LABEL authors="sofiavovchenko"

RUN apk add --no-cache \
  build-base \
  python3-dev \
  py3-setuptools \
  py3-pip \
  libffi-dev \
  mongodb-tools \
  && pip install --upgrade pip

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

COPY . /app

RUN mkdir -p /app/backend/rotten_scores/static_dev /app/backend/rotten_scores/templates

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup -S notroot && adduser -S imnotroot -G notroot
USER imnotroot

ENTRYPOINT ["/entrypoint.sh"]