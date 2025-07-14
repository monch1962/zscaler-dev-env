FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir zscaler-sdk-python

ENV HOVERFLY_VERSION 1.11.2 # Check for the latest stable version on Hoverfly GitHub releases
RUN curl -L [https://github.com/SpectoLabs/hoverfly/releases/download/v$](https://github.com/SpectoLabs/hoverfly/releases/download/v$){HOVERFLY_VERSION}/hoverctl-linux-amd64.tar.gz | tar -xz -C /usr/local/bin/
RUN mv /usr/local/bin/hoverctl-linux-amd64 /usr/local/bin/hoverctl

WORKDIR /app

ENV HTTP_PROXY="http://localhost:8500"
ENV HTTPS_PROXY="http://localhost:8500"
ENV NO_PROXY="localhost,127.0.0.1"

CMD ["bash"]
