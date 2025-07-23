# syntax=docker/dockerfile:1

FROM python:3.13-slim-bullseye

# Upgrade system packages to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get clean

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get upgrade -y && pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run"]