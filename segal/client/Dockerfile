FROM python:3.6-alpine

# TOOLS FOR INSTALLING LIBXML PYTHON MODULE FROM SOURCE
RUN apk add --update --no-cache python3-dev g++ libxml2-dev libxslt-dev libffi-dev openssl-dev

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./app /app
COPY ./certs /etc/ssl
