#!/bin/sh

# Copy (read only) config file from outside the container,
# into the container in the correct location.
cp /var/rpi-config/cgate-monitor/cbus_config.py   /python/cgate-monitor/cbus_config.py
cp /var/rpi-config/cgate-monitor/twitter.py       /python/cgate-monitor/twitter_config.py
cp /var/rpi-config/cgate-monitor/email_config.py  /python/cgate-monitor/email_config.py

# Start CGate Monitor
cd /python/cgate-monitor
/usr/local/bin/python3 cgate_monitor.py
