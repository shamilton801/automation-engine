FROM ubuntu:18.04
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install python3 python3-pip python3-opencv --yes
RUN pip3 install --upgrade pip