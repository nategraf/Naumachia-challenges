FROM ubuntu:xenial

RUN apt-get -y update \
    && apt-get -y install xinetd telnetd dnsutils git

# SET UP ENV
ARG USERNAME=noob
ARG PASSWORD=noob 
ARG SANDBOX_REPO=https://github.com/nategraf/wrastle.git
ARG CTF_FLAG=flag{houses_made_of_straw_blow_down_easy}

RUN useradd -Um $USERNAME && \
    printf "${PASSWORD}\n${PASSWORD}" | passwd $USERNAME

RUN cd /home/$USERNAME && \
    git clone $SANDBOX_REPO && \
    echo "$CTF_FLAG" > .ctf_flag

COPY ./etc/* /etc/
COPY ./entrypoint.sh /sbin/entrypoint.sh
RUN chmod +x /sbin/entrypoint.sh

EXPOSE 23

ENTRYPOINT ["entrypoint.sh"]
CMD ["xinetd", "-dontfork", "-inetd_compat"]
