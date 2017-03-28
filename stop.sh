sudo /sbin/service rabbitmq-server stop
sudo /etc/init.d/celeryd stop
uwsgi --stop /var/golden-speaker.pid
sudo nginx -s stop
