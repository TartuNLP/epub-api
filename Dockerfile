FROM python:3.9-alpine

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        gcc \
        g++ \
        libffi-dev \
        musl-dev \
        git

ENV PYTHONIOENCODING=utf-8
ENV CONFIGURATION=production
ENV ROOT_PATH=""

WORKDIR /app/data
WORKDIR /app

RUN adduser -D app && \
    chown -R app:app /app && \
    chown -R app:app /app/data
USER app
ENV PATH="/home/app/.local/bin:${PATH}"

VOLUME /app/data

COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app . .

EXPOSE 80

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

