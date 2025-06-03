FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/stackitcloud/certbot-dns-stackit.git /src
WORKDIR /src
RUN pip install --prefix=/install .

FROM certbot/certbot:v3.3.0

COPY --from=builder /install /usr/local
WORKDIR /etc/letsencrypt

ENTRYPOINT ["certbot"]
