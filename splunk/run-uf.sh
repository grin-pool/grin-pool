#!/bin/bash
# Add root group to splunk
usermod -a -G root splunk

# Deploy splunk via ansible
/sbin/entrypoint.sh start-and-exit

# Put our config in place
su - splunk -c "cp /configmap/* $SPLUNK_HOME/etc/system/local/"

(sleep 60 && $SPLUNK_HOME/bin/splunk restart) &

# Start the splunk forwarder
/sbin/entrypoint.sh start
