FROM alpine:latest
LABEL maintainer "me@micahrl.com"

# Intended to be set per environment
ENV SALACIOUSPATRONYM_CONSUMERTOKEN   replaceme
ENV SALACIOUSPATRONYM_CONSUMERSECRET  replaceme
ENV SALACIOUSPATRONYM_ACCESSTOKEN     replaceme
ENV SALACIOUSPATRONYM_ACCESSSECRET    replaceme

# Intended to enhance readability of my RUN statements
ENV LOGFILE /home/pat/salaciouspatronym.log
ENV ZIPURL https://github.com/mrled/salaciouspatronym/archive/master.zip

RUN /bin/true \
    && apk --no-cache upgrade && apk --no-cache add \
        python3 \
        ca-certificates \
        openssl \
    && python3 -m ensurepip \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install \
        tweepy \
    && addgroup -S pat \
    && adduser -S -G pat -s /bin/sh pat \
    && /bin/true

# NOTE: We do not use a USER statement, because crond (and therefore entrypoint.sh) must be run as root

# For local dev, uncomment these two lines and comment the wget line below
# COPY ["salacious_patronym.py", "/home/pat/salaciouspatronym/salacious_patronym.py"]
# RUN chown -R pat:pat /home/pat/salaciouspatronym

RUN /bin/true \
    && su -l -c "wget -q $ZIPURL && unzip master.zip && sleep 1 && mv salaciouspatronym-master salaciouspatronym" pat \

    # Initialize database, yes, but also initialize the logfile with correct permissions for 'pat' user
    && su -l -c "/usr/bin/python3 /home/pat/salaciouspatronym/salacious_patronym.py --debug --initialize reinit > $LOGFILE" pat \

    # 1. Copy relevant env vars into /etc/environment, which is shared for all users
    #    This file is NOT read automatically if you 'su - pat' in the container, but IS read automatically by cron (whatever)
    #    If necessary you can dot-source it like '. /etc/environment'
    # 2. Had to truncate log file with '>' IN THE ENTRYPOINT TOO, or else 'tail -f' will not follow changes to it, idk why
    && echo "env | grep SALACIOUSPATRONYM_ > /etc/environment; crond -b; echo Initializing... > $LOGFILE; tail -f $LOGFILE" > /bin/entrypoint.sh \
    && chmod 755 /bin/entrypoint.sh \

    # && echo "* * * * * echo \$SALACIOUSPATRONYM_CONSUMERTOKEN >> $LOGFILE" | crontab -u pat -
    && echo "* */6 * * * /usr/bin/python3 /home/pat/salaciouspatronym/salacious_patronym.py --sext --tweet 2>&1 >> $LOGFILE" | crontab -u pat - \

    && /bin/true

CMD ["/bin/sh", "-c", "/bin/entrypoint.sh"]
