from django.conf.urls import url
from mpd import views

urlpatterns = [
        url(r'^$', views.mpd, name='mpd'),
        url(r'^upload_audio', views.upload_audio, name='upload_audio'),

]