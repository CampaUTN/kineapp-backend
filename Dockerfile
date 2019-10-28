FROM python:3.7.4-stretch
ENV PYTHONUNBUFFERED=1
RUN mkdir /kinesio
ADD . /kinesio
WORKDIR /kinesio/kinesio

ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install --no-install-recommends -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

RUN pip install --upgrade pip && \
    pip install -r /kinesio/requirements.txt
