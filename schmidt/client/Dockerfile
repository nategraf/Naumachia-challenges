FROM python:3-alpine

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./client.py /usr/bin/client.py

STOPSIGNAL sigint
CMD ["python", "/usr/bin/client.py"]
