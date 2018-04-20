FROM ubuntu:xenial

RUN apt-get update && \
    apt-get -y install xinetd telnetd git automake build-essential libpam0g-dev libssl-dev

# BUILD PAM_NAUMOTP
ARG NAUMOTP_REPO_URL=https://github.com/nategraf/pam_naumotp.git
ARG NAUMOTP_REPO_BRANCH=master

COPY ./make-naumotp.sh ./make-naumotp.sh
RUN sh ./make-naumotp.sh

RUN apt-get -y remove automake build-essential && \
    apt-get -y autoremove

# SET UP ENV
ARG USERNAME=noob 
ARG PASSWORD=noob 
ARG NAUMOTP_SECRET=secret_key
ARG SANDBOX_REPO=https://github.com/nategraf/wrastle.git
ARG CTF_FLAG=flag{houses_made_of_sticks_are_hardly_better}

RUN useradd -Um $USERNAME && \
    printf "${PASSWORD}\n${PASSWORD}\n" | passwd $USERNAME

RUN cd /home/$USERNAME && \
    git clone $SANDBOX_REPO && \
    echo "$CTF_FLAG" > .ctf_flag

# Copy is done in two steps to avoid clobering all of pam.d
COPY ./etc/* /etc/
COPY ./pam.d/* /etc/pam.d/
RUN echo $NAUMOTP_SECRET > /home/$USERNAME/.naumotp_secret && \
    chmod 600 /home/$USERNAME/.naumotp_secret

EXPOSE 23

CMD ["xinetd", "-dontfork", "-inetd_compat"]
