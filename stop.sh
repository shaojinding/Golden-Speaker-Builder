sudo /sbin/service rabbitmq-server stop
sudo /etc/init.d/celeryd stop
uwsgi --stop /tmp/project-master.pid
sudo nginx -s stop
