FROM sameersbn/bind:9.16.1-20200524

COPY ./requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/cache/bind
COPY zonerender.py /usr/bin/
COPY zone.j2 named.conf.j2 ./

EXPOSE 53/udp 53/tcp
ENV WEBMIN_ENABLED=false
ENTRYPOINT ["python3", "/usr/bin/zonerender.py", "/sbin/entrypoint.sh"]
