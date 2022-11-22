#!/bin/bash
# installation of onficollect package
sudo mkdir -p /usr/local/share/python/InfoCollect
cd /usr/local/share/python/InfoCollect
sudo chown ${LOGNAME}: .
curl -sS https://github.com/tommiport5/InfoCollect/python

sudo mkdir -p /var/www/html/cgi-bin
cd /var/www/html
curl -sS https://github.com/tommiport5/InfoCollect/html
sudo chown www-data:www-data *
cd cgi-bin
ln -s /usr/local/share/python/InfoCollect/present_cgi.py present_cgi.py
sudo chown www-data:www-data *

sudo mkdir /var/lib/misc
sudo chown ${LOGNAME}: /var/lib/misc

cd /etc/systemd/user
sudo curl https://github.com/tommiport5/assets/infocollect.service
