FROM python:3-alpine

COPY client.py emails.sqlite /app/
COPY ssl/* /etc/ssl/

ENV TLS_CA=/etc/ssl/ca.naum.crt EMAILDB_PATH=/app/emails.sqlite

CMD ["python", "/app/client.py"]
