FROM python:3-alpine

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE 80
ENV PYTHONPATH=/app
WORKDIR /app
CMD ["gunicorn", "-b", "0.0.0.0:80", "-w", "1", "giulietta:app"]
