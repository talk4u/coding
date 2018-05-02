FROM python:3.6.5-alpine3.7
MAINTAINER Seungyong Lee <wdyd2004@naver.com>

# Install isolate

RUN set -eux \
    && apk add --no-cache --update \
    libcap-dev \
    git;

RUN set -eux \
    && git clone https://github.com/ioi/isolate.git /tmp/isolate \
    && make install -C /tmp/isolate \
    && rm -rf /tmp/isolate
