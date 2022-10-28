FROM ubuntu:latest
WORKDIR /app

RUN apt update && apt upgrade -y
RUN apt install -y git && apt install -y gnupg2 && apt install -y gnupg1
COPY requirements.txt requirements.txt


RUN apt install python3 python3-pip -y 

RUN pip3 install -r requirements.txt


COPY . .
COPY .env .env
EXPOSE 5432
#RUN sed -e "s/[#]\?listen_addresses = .*/listen_addresses = '*'/g" -i '/etc/postgresql/9.1/main/postgresql.conf'
CMD ["python3", "src/soteria.py"]
