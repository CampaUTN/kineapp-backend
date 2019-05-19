FROM python:3.7.3-stretch
RUN mkdir /kinesio
WORKDIR /kinesio
ADD . /kinesio
ENV PYTHONUNBUFFERED=0

RUN pip install --upgrade pip

RUN apt-get clean && \
apt-get update

RUN apt-get install --no-install-recommends -y build-essential apt-transport-https

RUN apt-get clean && \
apt-get update


RUN pip install -r /kinesio/pip_requirements.txt