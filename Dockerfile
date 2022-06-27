FROM python:3.10-alpine

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        gcc \
        g++ \
        libffi-dev \
        musl-dev \
        git

ENV PYTHONIOENCODING=utf-8

WORKDIR /app/data
WORKDIR /app

RUN addgroup -S app && \
    adduser -S -D -G app app && \
    chown -R app:app /app && \
    chown -R app:app /app/data

USER app
ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app . .

ARG API_VERSION
ENV API_VERSION=$API_VERSION

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

