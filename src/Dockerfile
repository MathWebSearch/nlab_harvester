FROM python:3.7.2-alpine3.9

RUN apk add --no-cache git g++ libxml2-dev libxslt-dev libxml2 libxslt

ADD ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV NLAB_HARVESTER_THREADS=1
ENV LATEXML_ADDRESS=localhost
ENV LATEXML_PORT=8080
ENV MAX_QUEUE_LENGTH=0
ENV UPDATE_FREQ=0

RUN mkdir -p /mws_nlab_harvester
WORKDIR /mws_nlab_harvester

RUN mkdir -p /mws_nlab_harvester/src
ADD ./*.py /mws_nlab_harvester/src/

RUN mkdir -p /mws_nlab_harvester/logs/

RUN mkdir -p /mws_nlab_harvester/harvests
ENV NLAB_HARVESTS=/mws_nlab_harvester/harvests/

RUN mkdir -p /mws_nlab_harvester/nlab-content-html/pages/
ENV NLAB_SOURCE=/mws_nlab_harvester/nlab-content-html/pages/

WORKDIR /mws_nlab_harvester/src
CMD ["python", "main.py"]
