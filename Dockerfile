FROM python:3.11-alpine
LABEL authors="sofiavovchenko"

RUN apt-get update && apt-get install -y \
  build-essential \
  python3-dev \
  python3-pip \
  python3-setuptools \
  && pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

COPY . /app

RUN mkdir -p /app/backend/rotten_scores/static_dev /app/backend/rotten_scores/templates

RUN groupadd --system notroot && useradd --system --create-home --gid notroot imnotroot
USER imnotroot

CMD python src/backend/rotten_scores/manage.py migrate && python src/backend/rotten_scores/manage.py runserver
