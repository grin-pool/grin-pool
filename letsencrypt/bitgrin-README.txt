Add this to the nginx image:



From within the nginx container:

apt-get update
apt-get install software-properties-common
add-apt-repository ppa:certbot/certbot && \
    set -ex && \
    apt-get -q --no-install-recommends --yes install \
    python-certbot-nginx
apt-get update
cd /etc/certs && ln -s certs/letsencrypt .
certbot renew
nginx -s reload

