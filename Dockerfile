FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update && apt upgrade
RUN apt install git

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN source .env # Load env variables

CMD ["python", "src/soteria.py"]