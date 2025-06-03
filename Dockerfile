FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install certbot

RUN git clone https://github.com/stackitcloud/certbot-dns-stackit.git /opt/certbot-dns-stackit \
    && pip install /opt/certbot-dns-stackit

WORKDIR /etc/letsencrypt

ENTRYPOINT ["certbot"]
