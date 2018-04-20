FROM python:3-alpine

COPY  requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY mailserver.py /app/
COPY ssl/* /etc/ssl/

ENV TLS_CERT=/etc/ssl/mail.democrats.ethihak.crt TLS_KEY=/etc/ssl/mail.democrats.ethihak.key

CMD ["python", "/app/mailserver.py"]
