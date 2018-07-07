FROM sameersbn/bind:9.9.5-20161106

COPY ./requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install -r requirements.txt

COPY zone-render-entrypoint.sh zone-render.py /sbin/
COPY zone.j2 named.conf.j2 ./

RUN chmod +x /sbin/zone-render-entrypoint.sh

ENTRYPOINT ["/sbin/zone-render-entrypoint.sh", "/sbin/entrypoint.sh"]
