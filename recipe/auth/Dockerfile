from python:3-alpine

COPY authserver.py requirements.txt users.yml /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN mkdir -p /home/topchef/recipes/public

CMD ["python", "/app/authserver.py"]
