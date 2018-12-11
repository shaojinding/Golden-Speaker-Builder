import base64
import json
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django_auth0.auth_decorator import login_required_auth0

# index page view
def mpd(request):
    context_dict = {}
    return render(request, 'mpd/mpd.html', context_dict)

# view for uploading annotations
@login_required_auth0()
@ensure_csrf_cookie
def upload_audio(request):
    if request.method == 'POST':
        recording_base64 = request.POST['recording']
        recording_blob = base64.b64decode(recording_base64)
        with open("{0}/{1}.wav".format('/home/burning/Project/golden-speaker/data/mpd', 'test'), "wb") as recording_file:
            recording_file.write(recording_blob)
    return HttpResponse('success')

# ajax get query utterances for database
@login_required_auth0()
def get_utterances(request):
    if request.method == 'GET':
        json_list = [1, 2, 3]
        json_file = json.dumps(json_list)
        return HttpResponse(json_file)