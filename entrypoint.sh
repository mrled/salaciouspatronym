#!/bin/sh

# The entrypoint for our Docker container

set -e
set -u
set -o pipefail

# Copy relevant env vars into /etc/environment, which is shared for all users
# NOTE: By itself, this file IS read by cron, but is NOT read by "su - USER"
#       Dockerfile adds a script in /etc/profile.d to make sure its read by ALL shells
env | grep SALLYPAT_ > /etc/environment

# Start the cron daemon in the background
crond -b

# Tweet once
su -l $SALLYPAT_USER -c "$SALLYPAT_DIR/salacious_patronym.py --debug --sext --tweet 2>&1 >> $SALLYPAT_LOGFILE"

# Echo the logfile to the container's stdout
tail -f $SALLYPAT_LOGFILE
