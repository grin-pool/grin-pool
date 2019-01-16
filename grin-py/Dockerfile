FROM docker.mwgrinpool.com:5001/mwdockerbase

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

WORKDIR /services

COPY grinbase/ /usr/local/bin/grinbase/
COPY grinlib/ /usr/local/bin/grinlib/
COPY services/*.py /usr/local/bin/
COPY services/config.ini /usr/local/bin/
COPY services/config.ini /services/
COPY api/ /usr/local/bin/api/
COPY api/MWGP_payout.py /content/

CMD ["/bin/sh"]
