from python:3-alpine

COPY ftpserver.py requirements.txt /app/
COPY ./recipes /home/topchef/recipes

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/ftpserver.py"]
