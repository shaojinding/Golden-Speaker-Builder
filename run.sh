sudo /sbin/service rabbitmq-server start
sudo /etc/init.d/celeryd start
uwsgi --ini speech_uwsgi.ini
sudo nginx
