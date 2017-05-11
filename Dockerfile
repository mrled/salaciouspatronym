FROM alpine:latest
LABEL maintainer "me@micahrl.com"

# Intended to be set per environment
ENV SALLYPAT_CONSUMERTOKEN   replaceme
ENV SALLYPAT_CONSUMERSECRET  replaceme
ENV SALLYPAT_ACCESSTOKEN     replaceme
ENV SALLYPAT_ACCESSSECRET    replaceme

# Configure tweet frequency. Valid values are:
# - once: Run crond, but do not schedule a tweet. Do tweet once when the container starts.
# - 01min: Every minute (Twitter might not like this)
# - 15min: Every 15 minutes (Twitter might not like this)
# - 1hour: Every hour
# - 6hour: Every 6 hours
# - devel: Log a salacious patronym every *minute*, but do not tweet
ENV SALLYPAT_FREQUENCY devel

# Intended to enhance readability of my Dockerfile and scripts
ENV SALLYPAT_USER sallypat
ENV SALLYPAT_DIR /srv/salaciouspatronym
ENV SALLYPAT_LOGFILE $SALLYPAT_DIR/salaciouspatronym.log

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
    # 'set -a' exports ALL env vars in these files, even if not prepended with 'export'
    && echo "set -a && . /etc/profile && set +a" > /etc/skel/.profile \
    && addgroup -S $SALLYPAT_USER \
    && adduser -S -G $SALLYPAT_USER -s /bin/sh $SALLYPAT_USER \
    && /bin/true

# NOTE: We do not use a USER statement, because crond (and therefore entrypoint.sh) must be run as root

COPY ["salacious_patronym.py", "$SALLYPAT_DIR/salacious_patronym.py"]
COPY ["entrypoint.sh", "/bin/"]
RUN /bin/true \

    && chown -R $SALLYPAT_USER:$SALLYPAT_USER $SALLYPAT_DIR \

    # Make all shells get the environment that is set in entrypoint.sh
    && touch /etc/environment \
    && echo ". /etc/environment" > /etc/profile.d/environment.sh \

    # Initialize database, yes, but also initialize the logfile with correct permissions for $SALLYPAT_USER
    && su -l $SALLYPAT_USER -c \
        "$SALLYPAT_DIR/salacious_patronym.py --debug --initialize reinit > $SALLYPAT_LOGFILE" \

    && /bin/true

CMD ["/bin/sh", "-c", "/bin/entrypoint.sh"]
