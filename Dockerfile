ARG TAG=3.11-slim

FROM python:$TAG

ARG CUSTOM_UID=1001
ARG CUSTOM_GID=1001

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="${PATH}:/opt/poetry/bin"

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - \
#    && pip install --upgrade \
#        pip \
#        pipenv \
    && addgroup --gid $CUSTOM_GID --system app \
    && adduser --home /home/app --shell /bin/bash --disabled-password --uid $CUSTOM_UID --system --group app

USER app

WORKDIR /app
