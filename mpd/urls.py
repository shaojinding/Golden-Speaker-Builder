from django.conf.urls import url
from mpd import views

urlpatterns = [
        url(r'^$', views.index, name='index_mpd'),
        url(r'^mpd', views.mpd, name='mpd'),
        url(r'^upload_audio', views.upload_audio, name='upload_audio'),
        url(r'^get_textgrid', views.get_textgrid, name='get_textgrid'),

]