#!/bin/bash
# installation of onficollect package
SCR=$(mktemp -dt tmpXXXXX)
cd $SCR
wget https://github.com/tommiport5/InfoCollect/archive/refs/heads/main.zip
unzip main.zip

cd InfoCollect-main/python

sudo mkdir -p /usr/local/share/python/InfoCollect
sudo mv * /usr/local/share/python/InfoCollect
sudo chown -R ${LOGNAME}: /usr/local/share/python/InfoCollect
sudo chmod 755 /usr/local/share/python/InfoCollect/*

cd ../html
sudo mkdir -p /var/www/html/cgi-bin
sudo mv * /var/www/html
sudo chown -R www-data:www-data /var/www/html
sudo ln -s /usr/local/share/python/InfoCollect/present_cgi.py /var/www/html/cgi-bin/present_cgi.py
sudo chown -R www-data:www-data /var/www/html

sudo mkdir /var/lib/misc
sudo chown ${LOGNAME}: /var/lib/misc

cd ../assets
sudo mv infocollect.service /etc/systemd/user

cd

rm -rf $SCR
