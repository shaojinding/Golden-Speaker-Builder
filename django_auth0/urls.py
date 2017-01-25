# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import auth_callback, log_out, log_in


urlpatterns = [
    url(r'callback/?$', auth_callback, name='auth_callback'),
    url(r'logout/$', log_out, name='logout'),
    url(r'login/$', log_in, name='login'),
]
