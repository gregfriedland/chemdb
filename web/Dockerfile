FROM ubuntu:latest

MAINTAINER Greg Friedland "greg.friedland@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev
# build-essential

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app/

EXPOSE 5000

CMD ["python3", "server.py"]
