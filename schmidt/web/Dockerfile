FROM python:3-alpine

RUN apk add --no-cache python3-dev

COPY ./app /usr/local/web
RUN pip install -r /usr/local/web/requirements.txt

EXPOSE 80
WORKDIR /usr/local/
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "web:app"]
