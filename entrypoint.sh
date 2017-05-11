#!/bin/sh
# The entrypoint for our Docker container

set -e
set -u
set -o pipefail

echo "Salacious' \"Patronym\" eggplant emoji"

# Copy relevant env vars into /etc/environment, which is shared for all users
# NOTE: By itself, this file IS read by cron, but is NOT read by "su - USER"
#       Dockerfile adds /etc/profile.d script for it to be read by ALL shells
env | grep SALLYPAT_ > /etc/environment

twinvoke="$SALLYPAT_DIR/salacious_patronym.py --debug --sext --tweet 2>&1 >> $SALLYPAT_LOGFILE"
dvinvoke="$SALLYPAT_DIR/salacious_patronym.py --debug --sext         2>&1 >> $SALLYPAT_LOGFILE"
cron01min='*    *   * * *'
cron15min='*/15 *   * * *'
cron1hour='0    *   * * *'
cron6hour='0    */6 * * *'

# Configure the crontab based on the frequency given by the environment
# Note that when we do 'crontab -' below, this *replaces* the existing crontab
# for our user; good in case we 'docker run' the container more than once
tweetonce=/bin/true
case "$SALLYPAT_FREQUENCY" in
    01min) crontab=$(echo "$cron01min $twinvoke");;
    15min) crontab=$(echo "$cron15min $twinvoke");;
    1hour) crontab=$(echo "$cron1hour $twinvoke");;
    6hour) crontab=$(echo "$cron6hour $twinvoke");;
    devel)
        crontab="$cron01min $dvinvoke"
        tweetonce=/bin/false
        ;;
    once)
        # Do nothing: we will tweet once at the end of this script
        crontab=""
        ;;
    *)
        echo "Unknown value for SALLYPAT_FREQUENCY variable '$SALLYPAT_FREQUENCY'"
        exit -1
        ;;
esac
echo "Setting crontab: "
echo "$crontab"
echo "$crontab" | crontab -u $SALLYPAT_USER -

# Start the cron daemon in the background
crond -b

# Tweet once
if $tweetonce; then su -l $SALLYPAT_USER -c "$twinvoke"; fi

# Echo the logfile to the container's stdout
tail -f $SALLYPAT_LOGFILE
