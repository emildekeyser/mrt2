#!/bin/bash -x

prefix=/usr/local/mrt2
mkdir -p $prefix
cp -rv ./* $prefix/
apt update
apt upgrade
apt install socat apache2
ln -sfv $prefix/webroot /var/www/html/mrt2
ln -sfv $prefix/src/apache-vhost.conf /etc/apache2/sites-available/mrt2.conf
a2dissite 000-default
a2ensite mrt2
a2enmod proxy proxy_http headers
systemctl reload apache2
useradd --shell /bin/none --home=/var/local/queueer --create-home queueer
chown -R queueer:queueer /var/www/html/mrt2
ln -sfv $prefix/src/crontab /etc/cron.d/queueserver
ln -sfv $prefix/src/queue_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now queue_server.service
systemctl status apache2
systemctl status queue_server
