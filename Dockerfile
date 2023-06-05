FROM python:3.9-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV POSTGRES_HOST='31.131.17.213'
ENV POSTGRES_PORT='5432'
ENV POSTGRES_USER='luka'
ENV POSTGRES_PASSWORD='QlWuEkRa'
ENV POSTGRES_DB='ur_db_prod'

COPY requirements.txt ./

RUN python -m venv /venv
ENV PATH='/venv/bin:$PATH'

RUN pip install -r requirements.txt

COPY . .
