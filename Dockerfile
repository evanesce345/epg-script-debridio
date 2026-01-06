FROM python:3.12-slim

WORKDIR /app

ENV TZ=America/New_York

COPY . .

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN crontab -u root crontab

ENTRYPOINT [ "/app/entrypoint.sh" ]