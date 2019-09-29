FROM python:3.7.4-stretch
ENV PYTHONUNBUFFERED=1
RUN mkdir /kinesio
ADD . /kinesio
WORKDIR /kinesio/kinesio

RUN pip install --upgrade pip && \
    pip install -r /kinesio/requirements.txt
