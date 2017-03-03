from django.conf.urls import url
from speech import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^start_record_session/(?P<anchor_set_name_slug>[\w\-]+)/$', views.start_record_session, name='start_record_session'),
        # url(r'^start_edit_session/(?P<anchor_set_name_slug>[\w\-]+)/$', views.start_edit_session, name='start_edit_session'),
        url(r'^record/(?P<phoneme>[\w\-]+)/$', views.record, name='record'),
        # url(r'^edit/(?P<phoneme>[\w\-]+)/$', views.edit, name='edit'),
        url(r'^finish_record_session', views.finish_record_session, name="finish_record_session"),
        url(r'build_sabr', views.build_sabr, name='build_sabr'),
        url(r'^build_synthesize', views.build_synthesize, name='build_synthesize'),
        url(r'^get_utterances', views.get_utterances, name='get_utterances'),
        url(r'^synthesize', views.synthesize, name='synthesize'),
        url(r'^practice/(?P<golden_speaker_name_slug>[\w\-]+)/$', views.practice, name='practice'),
        # url(r'^get_contained_utterances', views.get_contained_utterances, name='get_contained_utterances'),
        # url(r'^upload_record', views.upload_record, name='upload_record'),
        url(r'^upload_annotation', views.upload_annotation, name='upload_annotation'),
        url(r'^upload_pitch', views.upload_pitch, name='upload_pitch'),
        # url(r'^upload_edit_annotation', views.upload_edit_annotation, name='upload_edit_annotation'),
        url(r'^manage_anchorset', views.manage_anchorset, name='manage_anchorset'),
        url(r'^anchorset/(?P<anchor_set_name_slug>[\w\-]+)/$', views.anchorset, name='anchorset'),
        url(r'^add_anchorset', views.add_anchorset, name='add_anchorset'),
        url(r'^delete_anchorset/(?P<anchor_set_name_slug>[\w\-]+)/$', views.delete_anchorset, name='delete_anchorset'),
        url(r'^delete_golden_speaker/(?P<speaker_name_slug>[\w\-]+)/$', views.delete_golden_speaker, name='delete_golden_speaker'),
        url(r'^get_build_status', views.get_build_status, name='get_build_status'),
        url(r'^get_synthesize_status', views.get_synthesize_status, name='get_synthesize_status'),
]