FROM sameersbn/bind:9.9.5-20161106

COPY ./requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install -r requirements.txt

COPY zonerender.py /sbin/
COPY zone.j2 named.conf.j2 ./

EXPOSE 53/udp 53/tcp
ENV WEBMIN_ENABLED=false
ENTRYPOINT ["python3", "/sbin/zonerender.py", "/sbin/entrypoint.sh"]
