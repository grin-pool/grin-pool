#!/bin/bash

echo "Starting letsencrypt create or renew"
while /bin/true; do
    echo "Create or renew"
    if [ ! -e /etc/letsencrypt/live/$MYDOMAIN/fullchain.pem ]; then
        # Generate Certificates
        certbot certonly --nginx -n --agree-tos -m admin@$MYDOMAIN -d $MYDOMAIN -d api.$MYDOMAIN -d www.$MYDOMAIN -d stratum.$MYDOMAIN
        cp /${MYDOMAIN}/* /etc/nginx/conf.d/
        nginx -s reload
    else
        # Renew Certificates
        certbot renew --nginx -n --agree-tos -m admin@$MYDOMAIN
        if [ $? -eq 0 ]; then
            nginx -s reload
       fi
    fi
    if [ ! -e /etc/nginx/conf.d/${MYDOMAIN}.http.conf ]; then
        cp /${MYDOMAIN}/* /etc/nginx/conf.d/
        nginx -s reload
    fi
    sleep 1d
done
