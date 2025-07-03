FROM python:3.11-slim

WORKDIR /usr/src/dbt

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

EXPOSE 8080