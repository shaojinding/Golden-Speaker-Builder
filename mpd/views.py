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
            user.set_transcription_dir('data/mpd/transcriptions/{0}'.format(user.username))
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
    with open("static/doc/sentences.txt", "rb") as f:
        text = f.readlines()
    json_file = json.dumps(text)
    context_dict = {"sentences": json_file}
    return render(request, 'mpd/mpd.html', context_dict)

# view for uploading annotations
@ensure_csrf_cookie
def upload_audio(request):
    if request.method == 'POST':
        username = request.session['username']
        user = User.objects.get(username=username)
        recording_base64 = request.POST['recording']
        transcription = request.POST['transcription']
        utt_id = request.POST['utt_id']
        repeat_id = request.POST['repeat_id']
        recording_blob = base64.b64decode(recording_base64)
        with open("{0}/{1:04d}_{1:04d}.wav".format(user.wav_file_dir, int(utt_id), int(repeat_id)), "wb") as recording_file:
            recording_file.write(recording_blob)
        with open("{0}/{1:04d}_{1:04d}.txt".format(user.transcription_dir, int(utt_id), int(repeat_id)), "w") as transcription_file:
            transcription_file.write(transcription)
        # user.num_saved_recordings += 1
        # user.save()
    return HttpResponse('success')

# ajax get query utterances for database
def get_textgrid(request):
    if request.method == 'GET':
        utt_id = request.GET['utt_id']
        repeat_id = request.GET['repeat_id']
        username = request.session['username']
        user = User.objects.get(username=username)
        wav_dir = "{0}/{1:04d}_{1:04d}.wav".format(user.wav_file_dir, int(utt_id), int(repeat_id))
        trans_dir = "{0}/{1:04d}_{1:04d}.TextGrid".format(user.transcription_dir, int(utt_id), int(repeat_id))
        tg_dir = "{0}/{1:04d}_{1:04d}.TextGrid".format(user.textgrid_dir, int(utt_id), int(repeat_id))
        os.environ.update({'CONDA_PATH': '/root/anaconda3'})
        os.system('./run_mpd.sh {0} {1} {2}'.format(wav_dir, trans_dir, tg_dir))
        with open("{0}/{1:04d}_{1:04d}.TextGrid".format(user.textgrid_dir, int(utt_id), int(repeat_id)), "rb") as f:
            text = f.readlines()
        # with open("/home/burning/Project/golden-speaker/gsb-mpd/exp/temp/test.TextGrid", "rb") as f:
        #     text = f.readlines()
        text = remove_empty_lines(text)
        textgrid = TextGrid(text)
        tg_json = textgrid.toJson()
        # json_list = [1, 2, 3]
        # json_file = json.dumps(json_list)
        return HttpResponse(tg_json)
