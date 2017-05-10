FROM alpine:latest
LABEL maintainer "me@micahrl.com"

# Intended to be set per environment
ENV SALLYPAT_CONSUMERTOKEN   replaceme
ENV SALLYPAT_CONSUMERSECRET  replaceme
ENV SALLYPAT_ACCESSTOKEN     replaceme
ENV SALLYPAT_ACCESSSECRET    replaceme

# Intended to enhance readability of my Dockerfile and scripts
ENV SALLYPAT_USER sallypat
ENV SALLYPAT_DIR /srv/salaciouspatronym
ENV SALLYPAT_LOGFILE $SALLYPAT_DIR/salaciouspatronym.log
ENV SALLYPAT_ZIPURL https://github.com/mrled/salaciouspatronym/archive/master.zip
ENV SALLYPAT_ENTRY /bin/entrypoint.sh

RUN /bin/true \
    && apk --no-cache upgrade && apk --no-cache add \
        python3 \
        ca-certificates \
        openssl \
    && python3 -m ensurepip \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install \
        tweepy \
    && mkdir /etc/skel \
    # Not sure why it isn't doing this by default?
    # ('set -a' automatically exports *all* environment variables)
    && echo "set -a && . /etc/profile && set +a" > /etc/skel/.profile \
    && addgroup -S $SALLYPAT_USER \
    && adduser -S -G $SALLYPAT_USER -s /bin/sh $SALLYPAT_USER \
    && /bin/true

# NOTE: We do not use a USER statement, because crond (and therefore entrypoint.sh) must be run as root

# For local dev, uncomment this section:
COPY ["salacious_patronym.py", "$SALLYPAT_DIR/salacious_patronym.py"]
RUN chown -R $SALLYPAT_USER:$SALLYPAT_USER $SALLYPAT_DIR

# For prod, uncomment this section:
# RUN /bin/true \
#     && wget -q $ZIPURL -O /tmp/salaciouspatronym-master.zip \
#     && unzip /tmp/salaciouspatronym-master.zip -d /tmp \
#     # If we don't sleep here, the mv command fails sometimes, rolleyes emoji
#     && sleep 1 \
#     && mv /tmp/salaciouspatronym-master $SALLYPAT_DIR \
#     && chown -R $SALLYPAT_USER:$SALLYPAT_USER $SALLYPAT_DIR \
#     && /bin/true

RUN /bin/true \

    # Make all shells get the environment that is set in entrypoint.sh
    && touch /etc/environment \
    && echo ". /etc/environment" > /etc/profile.d/environment.sh \

    # Initialize database, yes, but also initialize the logfile with correct permissions for $SALLYPAT_USER
    && su -l $SALLYPAT_USER -c \
        "$SALLYPAT_DIR/salacious_patronym.py --debug --initialize reinit > $SALLYPAT_LOGFILE" \

    # && echo "* * * * * echo \$SALLYPAT_CONSUMERTOKEN >> $SALLYPAT_LOGFILE" | crontab -u $SALLYPAT_USER -
    && echo "   0 */6 * * * $SALLYPAT_DIR/salacious_patronym.py --debug --sext --tweet 2>&1 >> $SALLYPAT_LOGFILE" | \
        crontab -u $SALLYPAT_USER - \
    && echo "*/15 *   * * * $SALLYPAT_DIR/salacious_patronym.py --debug --test-twitter-access 2>&1 >> $SALLYPAT_LOGFILE" | \
        crontab -u $SALLYPAT_USER - \

    && /bin/true

COPY ["entrypoint.sh", "/bin/"]

CMD ["/bin/sh", "-c", "/bin/entrypoint.sh"]
