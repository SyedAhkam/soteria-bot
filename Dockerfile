FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update && apt upgrade -y
RUN apt install -y git

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
COPY .env .env

RUN ./.env

CMD ["python", "src/soteria.py"]