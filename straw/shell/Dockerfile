FROM ubuntu:xenial

RUN apt-get -y update \
    && apt-get -y install xinetd telnetd git

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

EXPOSE 23

CMD ["xinetd", "-dontfork", "-inetd_compat"]
