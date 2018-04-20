FROM ubuntu:xenial
RUN apt-get update &&\
    apt-get install python3-pip xvfb git software-properties-common -y &&\
    apt-get install software-properties-common -y &&\
    add-apt-repository ppa:thopiekar/pyside-git -y &&\
    apt-get remove software-properties-common -y &&\
    apt-get update &&\
    apt-get install python3-pyside2 python3-lxml -y &&\
    apt-get clean

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt &&\
    pip3 install ghost.py==2.0.0.dev0 --pre

COPY ./client.py /app/client.py

CMD ["python3", "/app/client.py"]
