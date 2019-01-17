import base64
import json
from .forms import UsernameForm
from .models import User
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django_auth0.auth_decorator import login_required_auth0
from textgrid.parse_textgrid import TextGrid, remove_empty_lines
import os


# index page view
def index(request):
    if request.method == 'POST':
        username_form = UsernameForm(data=request.POST)
        if username_form.is_valid():
            user = username_form.save(commit=False)
            request.session['username'] = user.username
            user.set_wav_file_dir('data/mpd/recordings/{0}'.format(user.username))
            user.set_textgrid_dir('data/mpd/textgrids/{0}'.format(user.username))
            user.save()
            return redirect('/mpd/mpd')
        else:
            messages.error(request, 'Anchor set name should only contain A-Z, a-z, 0-9 and _')
            username_form = UsernameForm()
            context_dict = {'username_form': username_form}
            return render(request, 'mpd/index.html', context_dict)
    else:
        username_form = UsernameForm()
        context_dict = {'username_form': username_form}
        return render(request, 'mpd/index.html', context_dict)

def mpd(request):
    context_dict = {}
    return render(request, 'mpd/mpd.html', context_dict)

# view for uploading annotations
@login_required_auth0()
@ensure_csrf_cookie
def upload_audio(request):
    if request.method == 'POST':
        username = request.session['username']
        user = User.objects.get(username=username)
        recording_base64 = request.POST['recording']
        recording_blob = base64.b64decode(recording_base64)
        # with open("{0}/{1:04d}.wav".format(user.wav_file_dir, user.num_saved_recordings), "wb") as recording_file:
        #     recording_file.write(recording_blob)
        user.num_saved_recordings += 1
        user.save()
    return HttpResponse('success')

# ajax get query utterances for database
@login_required_auth0()
def get_textgrid(request):
    if request.method == 'GET':
        utt_id = request.GET['utt_id']
        username = request.session['username']
        user = User.objects.get(username=username)
        wav_dir = "{0}/{1:04d}.wav".format(user.wav_file_dir, int(utt_id))
        trans_dir = "gsb-mpd/src/script/../../test/data/test_mono_channel.txt"
        tg_dir = "{0}/{1:04d}.TextGrid".format(user.textgrid_dir, int(utt_id))
        os.environ.update({'CONDA_PATH': '/home/burning/Tools/anaconda2'})
        os.system('./gsb-mpd/run_mpd.sh {0} {1} {2}'.format(wav_dir, trans_dir, tg_dir))
        with open("{0}/{1:04d}.TextGrid".format(user.textgrid_dir, int(utt_id)), "rb") as f:
            text = f.readlines()
        text = remove_empty_lines(text)
        textgrid = TextGrid(text)
        tg_json = textgrid.toJson()
        # json_list = [1, 2, 3]
        # json_file = json.dumps(json_list)
        return HttpResponse(tg_json)