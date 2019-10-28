FROM python:3.7.4-stretch
ENV PYTHONUNBUFFERED=1
RUN mkdir /kinesio
ADD . /kinesio
WORKDIR /kinesio/kinesio

RUN echo "America/Argentina/Buenos_Aires" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && \
    apt-get install --no-install-recommends -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

RUN pip install --upgrade pip && \
    pip install -r /kinesio/requirements.txt
