FROM ubuntu

RUN apt-get update &&\
    apt-get install -y python3 apache2 &&\
    apt-get clean

RUN useradd -Um httpd && \
    printf "cubswin\ncubswin" | passwd httpd

COPY backdoor.py entrypoint.sh /tmp/
COPY envvars /etc/apache2/envvars
COPY html /var/www/html
COPY flag.txt /home/httpd
RUN mkdir -p /var/run/apache2 /var/lock/apache2 /var/log/apache2 &&\
    chown httpd:httpd -R /var/*/apache2 /var/www /tmp/backdoor.py /tmp/entrypoint.sh /home/httpd &&\
    setcap cap_net_bind_service+eip /usr/sbin/apache2

USER httpd
WORKDIR /home/httpd

EXPOSE 80
ENTRYPOINT ["/bin/sh", "/tmp/entrypoint.sh"]
CMD ["apachectl", "-D", "FOREGROUND"]
