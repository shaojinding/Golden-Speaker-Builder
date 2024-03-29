import base64
import json
import os
from copy import deepcopy
from shutil import copyfile, rmtree
from time import time

import numpy as np
import scipy.io.wavfile
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

# from gsb_sabr_api.tasks import build_sabr_model, synthesize_sabr
from gsb_ppg_gmm_api.tasks import data_preprocess, gmm_synthesize
from django_auth0.auth_decorator import login_required_auth0
from models import User, AnchorSet, Anchor, SourceModel, Utterance, GoldenSpeaker
from .forms import AnchorSetForm, RenameAnchorSetForm, InputTempoScaleForm

from pydub import AudioSegment


# index page view
def index(request):
    if 'profile' in request.session:  # log in
        user = request.session['profile']
        context_dict = {'name': user['nickname'], 'is_login': True}
    else:  # don't log in
        context_dict = {'is_login': False}
    return render(request, 'speech/index.html', context_dict)


# manage anchor set page view
@login_required_auth0()
def manage_anchorset(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchorset_list = AnchorSet.objects.order_by('-timestamp').filter(user=user)
    building_anchor_set = []
    timestamps = []
    for anchorset in anchorset_list:
        timestamps.append(anchorset.timestamp)
        if anchorset.built == 'In processing':
            building_anchor_set.append(anchorset.slug)
    json_building_anchor_set = json.dumps(building_anchor_set)
    json_timestamps = json.dumps(timestamps)
    context_dict = {'anchorsets': anchorset_list, 'name': username, 'is_login': True,
                    'building_anchor_set': json_building_anchor_set, 'timestamps': json_timestamps}
    return render(request, 'speech/manage_anchorset.html', context_dict)


@login_required_auth0()
def abort_anchorset(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    anchor_set.aborted = True
    anchor_set.built = "False"
    anchor_set.save()
    return redirect('/speech/manage_anchorset')


# anchor set detail page view
@login_required_auth0()
def anchorset(request, anchor_set_name_slug):
    context_dict = {}
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    context_dict['anchor_set_name'] = anchor_set.anchor_set_name
    anchors = Anchor.objects.filter(anchor_set=anchor_set)
    context_dict['anchors'] = anchors
    context_dict['anchor_set'] = anchor_set
    context_dict['name'] = username
    context_dict['is_login'] = True
    saved_phonemes = anchor_set.get_saved_phonemes()
    json_saved_phoneme = json.dumps(saved_phonemes)
    context_dict['saved_phonemes'] = json_saved_phoneme
    return render(request, 'speech/anchorset.html', context_dict)


# add anchor set page view
@login_required_auth0()
def add_anchorset(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if request.method == 'POST':
        anchorset_form = AnchorSetForm(data=request.POST)
        if anchorset_form.is_valid():
            try:
                anchorset = anchorset_form.save(commit=False)
                anchorset.active = False
                anchorset.completed = False
                anchorset.modified = False
                anchorset.built = "False"
                anchorset.user = user
                anchorset.aborted = False
                anchorset.timestamp = time()
                # anchorset.timestamp = strftime("%b %d %Y %H:%M:%S", gmtime())
                anchorset.set_saved_phonemes([])
                anchorset.save()
                anchorset.set_wav_file_dir('data/recordings/{0}/{1}'.format(username, anchorset.slug))
                anchorset.set_cached_file_dir('data/cache/{0}/{1}'.format(username, anchorset.slug))
                anchorset.set_pitch_model_dir('data/pitch_model/{0}/{1}.mat'.format(username, anchorset.slug))
                anchorset.save()
                return redirect('/speech/start_record_session/{}'.format(anchorset.slug))
            except:
                messages.error(request, 'You have had an anchor set with the this name')
                anchorset_form = AnchorSetForm()
                context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True}
                return render(request, 'speech/add_anchorset.html', context_dict)
        else:
            messages.error(request, 'Anchor set name should only contain A-Z, a-z, 0-9 and _')
            anchorset_form = AnchorSetForm()
            context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True}
            return render(request, 'speech/add_anchorset.html', context_dict)
    else:
        anchorset_form = AnchorSetForm()
        context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True}
        return render(request, 'speech/add_anchorset.html', context_dict)

@login_required_auth0()
def rename_anchorset(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    if request.method == 'POST':
        anchorset_form = AnchorSetForm(data=request.POST)
        if anchorset_form.is_valid():
            try:
                new_anchorset = anchorset_form.save(commit=False)
                new_anchorset.active = False
                new_anchorset.completed = anchorset.completed
                new_anchorset.modified = False
                new_anchorset.built = anchorset.built
                new_anchorset.user = user
                new_anchorset.aborted = anchorset.aborted
                new_anchorset.timestamp = anchorset.timestamp
                # anchorset.timestamp = strftime("%b %d %Y %H:%M:%S", gmtime())
                new_anchorset.set_saved_phonemes(anchorset.get_saved_phonemes())
                new_anchorset.save()

                new_anchorset.set_wav_file_dir('data/recordings/{0}/{1}'.format(username, new_anchorset.slug))
                new_anchorset.set_cached_file_dir('data/cache/{0}/{1}'.format(username, new_anchorset.slug))
                new_anchorset.cached_file_paths = anchorset.cached_file_paths
                new_anchorset.set_pitch_model_dir('data/pitch_model/{0}/{1}.mat'.format(username, new_anchorset.slug))

                new_anchorset.save()
                copy_anchorset_files(anchorset, new_anchorset, user)

                # remove files in the old anchorset
                if 'current_anchorset' in request.session:
                    if request.session['current_anchorset'] == anchorset.slug:
                        del request.session['current_anchorset']
                # remove pitch model
                if os.path.exists(anchorset.pitch_model_dir):
                    os.remove(anchorset.pitch_model_dir)
                # remove all the cached files
                if os.path.exists(anchorset.cached_file_dir):
                    rmtree(anchorset.cached_file_dir)
                if os.path.exists(anchorset.wav_file_dir):
                    rmtree(anchorset.wav_file_dir)
                AnchorSet.objects.filter(slug=anchorset.slug, user=user).delete()
                return redirect('/speech/manage_anchorset')
            except:
                messages.error(request, 'You have had an anchor set with the this name')
                anchorset_form = RenameAnchorSetForm()
                context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True,
                                'slug': anchor_set_name_slug}
                return render(request, 'speech/rename_anchorset.html', context_dict)
        else:
            messages.error(request, 'Anchor set name should only contain A-Z, a-z, 0-9 and _')
            anchorset_form = RenameAnchorSetForm()
            context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True,
                            'slug': anchor_set_name_slug}
            return render(request, 'speech/rename_anchorset.html', context_dict)
    else:
        anchorset_form = RenameAnchorSetForm()
        context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True,
                        'slug': anchor_set_name_slug}
        return render(request, 'speech/rename_anchorset.html', context_dict)


@login_required_auth0()
def copy_anchorset(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    if request.method == 'POST':
        anchorset_form = AnchorSetForm(data=request.POST)
        if anchorset_form.is_valid():
            # try:
            new_anchorset = anchorset_form.save(commit=False)
            new_anchorset.active = False
            new_anchorset.completed = anchorset.completed
            new_anchorset.modified = False
            new_anchorset.built = anchorset.built
            new_anchorset.user = user
            new_anchorset.aborted = anchorset.aborted
            new_anchorset.timestamp = time()
            # anchorset.timestamp = strftime("%b %d %Y %H:%M:%S", gmtime())
            new_anchorset.set_saved_phonemes(anchorset.get_saved_phonemes())
            new_anchorset.save()

            new_anchorset.set_wav_file_dir('data/recordings/{0}/{1}'.format(username, new_anchorset.slug))
            new_anchorset.set_cached_file_dir('data/cache/{0}/{1}'.format(username, new_anchorset.slug))
            new_anchorset.cached_file_paths = anchorset.cached_file_paths
            new_anchorset.set_pitch_model_dir('data/pitch_model/{0}/{1}.mat'.format(username, new_anchorset.slug))

            new_anchorset.save()

            copy_anchorset_files(anchorset, new_anchorset, user)
            return redirect('/speech/manage_anchorset')
            # except:
            #     messages.error(request, 'You have had an anchor set with the this name')
            #     anchorset_form = RenameAnchorSetForm()
            #     context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True, 'slug': anchor_set_name_slug}
            #     return render(request, 'speech/copy_anchorset.html', context_dict)
        else:
            messages.error(request, 'Anchor set name should only contain A-Z, a-z, 0-9 and _')
            anchorset_form = RenameAnchorSetForm()
            context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True, 'slug': anchor_set_name_slug}
            return render(request, 'speech/copy_anchorset.html', context_dict)
    else:
        anchorset_form = RenameAnchorSetForm()
        context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True, 'slug': anchor_set_name_slug}
        return render(request, 'speech/copy_anchorset.html', context_dict)


def copy_anchorset_files(old_anchorset, new_anchorset, user):
    # Copy pitch model file
    if os.path.exists(old_anchorset.pitch_model_dir):
        copyfile(old_anchorset.pitch_model_dir, new_anchorset.pitch_model_dir)
    for anchor in Anchor.objects.filter(anchor_set=old_anchorset):
        new_anchor = deepcopy(anchor)
        new_anchor.pk = None
        new_anchor.id = None
        new_anchor.anchor_set = new_anchorset
        new_anchor.record_name = anchor.record_name
        new_anchor.save()
        old_record_path = os.path.join(old_anchorset.wav_file_dir, '{}.wav'.format(anchor.record_name))
        new_record_path = os.path.join(new_anchorset.wav_file_dir, '{}.wav'.format(anchor.record_name))
        copyfile(old_record_path, new_record_path)
        old_cache_path = os.path.join(old_anchorset.cached_file_dir, '{}.mat'.format(anchor.record_name))
        if os.path.exists(old_cache_path):
            new_cache_path = os.path.join(new_anchorset.cached_file_dir, '{}.mat'.format(anchor.record_name))
            copyfile(old_cache_path, new_cache_path)


# delete anchor set operation view
@login_required_auth0()
def delete_anchorset(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if 'current_anchorset' in request.session:
        if request.session['current_anchorset'] == anchor_set_name_slug:
            del request.session['current_anchorset']
    anchorset = AnchorSet.objects.filter(slug=anchor_set_name_slug, user=user)[0]
    if os.path.exists(anchorset.pitch_model_dir):
        os.remove(anchorset.pitch_model_dir)
    if os.path.exists(anchorset.cached_file_dir):
        rmtree(anchorset.cached_file_dir)
    if os.path.exists(anchorset.wav_file_dir):
        rmtree(anchorset.wav_file_dir)
    AnchorSet.objects.filter(slug=anchor_set_name_slug, user=user).delete()
    return redirect('/speech/manage_anchorset')


# start record session operation view
@login_required_auth0()
def start_record_session(request, anchor_set_name_slug):
    request.session['current_anchorset'] = anchor_set_name_slug
    return redirect('/speech/record/index')


# record and annotate page view
@login_required_auth0()
def record(request, phoneme):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set_name_slug = request.session['current_anchorset']
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    saved_phonemes = anchor_set.get_saved_phonemes()
    json_saved_phoneme = json.dumps(saved_phonemes)
    num_phoneme = 40
    if len(anchor_set.get_saved_phonemes()) >= num_phoneme:
        anchor_set.completed = True
        anchor_set.save()
    completed = anchor_set.completed

    with open('static/doc/sentences.txt', 'r') as pitch_f:
        pitch_f = pitch_f.readlines()
    pitch_sentences = []
    for line in pitch_f:
        pitch_sentences.append(line.strip())
    json_pitch_sentences = json.dumps(pitch_sentences)

    if phoneme in saved_phonemes:
        anchor = Anchor.objects.get(anchor_set=anchor_set, record_name=phoneme)
        record_name = anchor.record_name
        with open("{0}/{1}.wav".format(anchor_set.wav_file_dir, record_name), "rb") as recording_file:
            recording_blob = recording_file.read()
        recording_base64 = base64.b64encode(recording_blob)
        json_record_details = json.dumps([anchor.L, anchor.R, anchor.C, recording_base64])
        context_dict = {'name': username, 'is_login': True,
                        'phoneme': phoneme, 'record_details': json_record_details,
                        'saved_phoneme': json_saved_phoneme, 'completed': completed,
                        'pitch_sentences': json_pitch_sentences}
    else:
        context_dict = {'name': username, 'is_login': True,
                        'phoneme': phoneme, 'record_details': "[]",
                        'saved_phoneme': json_saved_phoneme, 'completed': completed,
                        'pitch_sentences': json_pitch_sentences}
    return render(request, 'speech/record.html', context_dict)


# # anchor set recording finished, pitch recording page
# @login_required_auth0()
# def finish_record_session(request):
#     username = request.session['profile']['nickname']
#     user = User.objects.get(user_name=username)
#     anchor_set_name_slug = request.session['current_anchorset']
#     anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
#     num_phoneme = 40
#     if len(anchor_set.get_saved_phonemes()) >= num_phoneme:
#         # del request.session['current_anchorset']
#         anchor_set.completed = True
#         # anchor_set.aborted = False
#         anchor_set.save()
#     else:
#         messages.add_message(request, messages.INFO,
#                              'You did not finish recording '
#                              'all anchor sets, please finish them first.')
#         return redirect('/speech/record/index')
#     pitch_path = anchor_set.pitch_path
#     with open('static/doc/pitch.txt', 'r') as pitch_f:
#         pitch_doc = pitch_f.readline()
#     if os.path.exists(pitch_path):
#         with open(pitch_path, "rb") as recording_file:
#             recording_blob = recording_file.read()
#         recording_base64 = base64.b64encode(recording_blob)
#         context_dict = {'anchor_set_name': anchor_set.anchor_set_name, 'name': username, 'is_login': True,
#                         'pitch_file': recording_base64, 'pitch_doc': pitch_doc}
#     else:
#         context_dict = {'anchor_set_name': anchor_set.anchor_set_name, 'name': username, 'is_login': True,
#                         'pitch_file': None, 'pitch_doc': pitch_doc}
#
#     return render(request, 'speech/finish_record.html', context_dict)


# view for uploading annotations
@login_required_auth0()
@ensure_csrf_cookie
def upload_annotation(request):
    if request.method == 'POST':
        L = request.POST['L']
        R = request.POST['R']
        C = request.POST['C']
        phoneme = request.POST['phoneme']
        re_record = request.POST['re_record']
        if L and R and C and phoneme:
            username = request.session['profile']['nickname']
            user = User.objects.get(user_name=username)
            anchor_set_name_slug = request.session['current_anchorset']
            anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
            saved_phonemes = anchorset.get_saved_phonemes()
            if phoneme in saved_phonemes:
                anchor = Anchor.objects.get(anchor_set=anchorset, record_name=phoneme)
                anchorset.modified = True
                anchorset.save()
                anchor.L = L
                anchor.R = R
                anchor.C = C
                anchor.save()
                if re_record == 'true':
                    recording_base64 = request.POST['recording']
                    recording_blob = base64.b64decode(recording_base64)
                    record_name = anchor.record_name
                    with open("{0}/{1}.wav".format(anchorset.wav_file_dir, record_name), "wb") as recording_file:
                        recording_file.write(recording_blob)
            else:
                anchor = Anchor(anchor_set=anchorset, record_name=phoneme, L=L, R=R, C=C)
                anchor.save()
                recording_base64 = request.POST['recording']
                saved_phonemes.append(phoneme)
                request.session['saved_phonemes'] = saved_phonemes
                anchorset.set_saved_phonemes(saved_phonemes)
                anchorset.save()
                recording_blob = base64.b64decode(recording_base64)
                with open("{0}/{1}.wav".format(anchorset.wav_file_dir, anchor.record_name), "wb") as recording_file:
                    recording_file.write(recording_blob)
    return HttpResponse('success')


# # view for uploading pitch
# @login_required_auth0()
# @ensure_csrf_cookie
# def upload_pitch(request):
#     if request.method == 'POST':
#         username = request.session['profile']['nickname']
#         user = User.objects.get(user_name=username)
#         anchor_set_name_slug = request.session['current_anchorset']
#         current_anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
#         pitch_path = current_anchorset.pitch_path
#         pitch_base64 = request.POST['recording']
#         pitch_blob = base64.b64decode(pitch_base64)
#         with open(pitch_path, "wb") as recording_file:
#             recording_file.write(pitch_blob)
#         current_anchorset.modified = True
#         current_anchorset.save()
#     return HttpResponse('sucess')

# view for building sabr model
@login_required_auth0()
def cache_utterances(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set_name_slug = request.session['current_anchorset']
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    num_phoneme = 40
    if len(anchor_set.get_saved_phonemes()) >= num_phoneme:
        # del request.session['current_anchorset']
        anchor_set.completed = True
        # anchor_set.aborted = False
        anchor_set.save()
    else:
        messages.add_message(request, messages.INFO,
                             'You did not finish recording '
                             'all anchor sets, please finish them first.')
        return redirect('/speech/record/index')
    if anchor_set.built == 'Built' and not anchor_set.modified:
        return redirect('/speech')
    anchor_set.built = 'In processing'
    anchor_set.modified = False
    anchor_set.save()
    anchors = Anchor.objects.filter(anchor_set=anchor_set).order_by('record_name')
    audio_paths = []
    left = []
    right = []
    output_mat_path = anchor_set.cached_file_dir
    if os.listdir(output_mat_path):
        rmtree(output_mat_path)
        os.makedirs(output_mat_path)
    pitch_model_path = anchor_set.pitch_model_dir
    for anchor in anchors:
        audio_paths.append("{0}/{1}.wav".format(anchor_set.wav_file_dir, anchor.record_name))
        left.append(anchor.L)
        right.append(anchor.R)
    # build_sabr_model.delay(username, anchor_set_name_slug, audio_paths, left, right, output_mat_path)
    data_preprocess.delay(username, anchor_set_name_slug, audio_paths, left, right, output_mat_path, pitch_model_path)
    return redirect('/speech')

# view for building sabr model
@login_required_auth0()
def re_cache_utterances(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    anchor_set.built = 'In processing'
    anchor_set.modified = False
    anchor_set.save()
    anchors = Anchor.objects.filter(anchor_set=anchor_set).order_by('record_name')
    audio_paths = []
    left = []
    right = []
    output_mat_path = anchor_set.cached_file_dir
    pitch_model_path = anchor_set.pitch_model_dir
    for anchor in anchors:
        audio_paths.append("{0}/{1}.wav".format(anchor_set.wav_file_dir, anchor.record_name))
        left.append(anchor.L)
        right.append(anchor.R)
    data_preprocess.delay(username, anchor_set_name_slug, audio_paths, left, right, output_mat_path, pitch_model_path)
    return redirect('/speech/manage_anchorset/')


# page to choose source and target anchor set, and choose utterance to be built
@login_required_auth0()
def build_synthesize(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    source_models = SourceModel.objects.all()
    anchor_sets = AnchorSet.objects.filter(user=user, built='Built')
    utterances = Utterance.objects.all()
    tempo_scale_form = InputTempoScaleForm()
    context_dict = {'name': username, 'is_login': True, 'source_models': source_models,
                    'anchor_sets': anchor_sets, 'utterances': utterances, 'tempo_scale_form': tempo_scale_form}
    return render(request, 'speech/build_synthesize.html', context_dict)


# ajax get query utterances for database
@login_required_auth0()
def get_utterances(request):
    if request.method == 'GET':
        source_model_name_slug = request.GET['source_model']
        source_model = SourceModel.objects.get(slug=source_model_name_slug)
        utterances = Utterance.objects.filter(source_model=source_model)
        names = [u.name for u in utterances]
        trans = [u.transcription for u in utterances]
        weeks = [u.week for u in utterances]
        json_list = [names, trans, weeks]
        json_file = json.dumps(json_list)
        return HttpResponse(json_file)


# TODO: query for building status
@login_required_auth0()
def get_build_status(request):
    if request.method == 'GET':
        username = request.session['profile']['nickname']
        user = User.objects.get(user_name=username)
        slug = request.GET['slug']
        anchorset = AnchorSet.objects.get(slug=slug, user=user)
        built = anchorset.built
        # if built == 'Error':
        #     anchorset.built = 'False'
        #     anchorset.save()
        name = anchorset.anchor_set_name
        json_list = [name, built]
        json_file = json.dumps(json_list)
        return HttpResponse(json_file)


# view for synthesize
@login_required_auth0()
@ensure_csrf_cookie
def synthesize(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if request.method == 'POST':
        select_names_string = request.POST['select_names']
        select_weeks_string = request.POST['select_weeks']
        source_model_name = request.POST['source_model']
        target_model_name = request.POST['target_model']
        if select_names_string and source_model_name and target_model_name:
            select_names = select_names_string.strip().split(',')
            select_weeks = select_weeks_string.strip().split(',')
            source_model = SourceModel.objects.get(model_name=source_model_name)
            target_model = AnchorSet.objects.get(anchor_set_name=target_model_name, user=user)
            target_model_name_slug = target_model.slug
            timestamp = str(time())
            gs_name = source_model_name + '-' + target_model_name_slug + '-' + timestamp.replace('.', '-')
            gmm_model_path = os.path.join('data/gmm_model', '{0}_{1}.mat'.format(source_model_name, target_model_name_slug))
            gs = GoldenSpeaker(speaker_name=gs_name, source_model=source_model, anchor_set=target_model,
                               user=user, timestamp=timestamp, status="Synthesizing", aborted=False, gmm_model_path=gmm_model_path)
            gs.save()
            for name in select_names:
                uttr = Utterance.objects.get(name=name, source_model=source_model)
                gs.contained_utterance.add(uttr)
            gs.save()

            output_wav_dir = os.path.join('data/output_wav', username, gs.slug)
            gs.set_output_wav_dir(output_wav_dir)
            gs.save()

            # Prepare inputs to synthesize function
            # Remove week temporally since there is no folder for week for now
            utt_paths = [os.path.join('static/ARCTIC', source_model_name, 'test/mat', '{}.mat'.format(name))
                         for name, week in zip(select_names, select_weeks)]
            source_utt_paths = source_model.get_cached_file_paths()
            target_utt_paths = target_model.get_cached_file_paths()
            src_pitch_model_path = source_model.pitch_model_dir
            tgt_pitch_model_path = target_model.pitch_model_dir
            gmm_synthesize.delay(username, gs_name, utt_paths, gmm_model_path, source_utt_paths, target_utt_paths,
                       src_pitch_model_path, tgt_pitch_model_path, output_wav_dir)

    return redirect('/speech/practice/index')


# view for synthesize
@login_required_auth0()
def resynthesize(request, speaker_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    gs = GoldenSpeaker.objects.get(user=user, slug=speaker_name_slug)
    output_wav_dir = gs.output_wav_dir
    source_model = gs.source_model
    source_model_name = source_model.model_name
    gmm_model_path = gs.gmm_model_path
    gs_name = gs.speaker_name
    gs.status = "Synthesizing"
    gs.save()
    target_model = gs.anchor_set

    utterances = gs.contained_utterance.all()
    select_names = [u.name for u in utterances]
    select_weeks = [u.week for u in utterances]
    utt_paths = [os.path.join('static/ARCTIC', source_model_name, 'test/mat', '{}.mat'.format(name))
                 for name, week in zip(select_names, select_weeks)]
    source_utt_paths = source_model.get_cached_file_paths()
    target_utt_paths = target_model.get_cached_file_paths()
    src_pitch_model_path = source_model.pitch_model_dir
    tgt_pitch_model_path = target_model.pitch_model_dir
    gmm_synthesize.delay(username, gs_name, utt_paths, gmm_model_path, source_utt_paths, target_utt_paths,
                         src_pitch_model_path, tgt_pitch_model_path, output_wav_dir)
    return redirect('/speech/practice/index')

@login_required_auth0()
def abort_synthesize(request, speaker_name_slug):
    gs = GoldenSpeaker.objects.get(slug=speaker_name_slug)
    gs.aborted = True
    gs.save()
    return redirect('/speech/manage_anchorset')


# view for practice
@login_required_auth0()
def practice(request, golden_speaker_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if golden_speaker_name_slug == 'index':
        if_choose = True
        gss = GoldenSpeaker.objects.order_by('-timestamp').filter(user=user)
        building_gs = []
        timestamps = []
        for gs in gss:
            timestamps.append(gs.timestamp)
            if gs.status == 'Synthesizing':
                building_gs.append(gs.slug)
        json_timestamps = json.dumps(timestamps)
        json_building_gs = json.dumps(building_gs)
        context_dict = {'name': username, 'is_login': True, 'if_choose': if_choose,
                        'golden_speakers': gss, 'building_golden_speakers': json_building_gs,
                        'timestamps': json_timestamps}
    else:
        if_choose = False
        uttr_files = {}
        gs = GoldenSpeaker.objects.get(slug=golden_speaker_name_slug)
        uttrs = Utterance.objects.filter(goldenspeaker=gs)
        for uttr in uttrs:
            uttr_path = '{0}/{1}.wav'.format(gs.output_wav_dir, uttr.name)
            # uttr_path = 'data/output_wav/{0}/{1}/{2}.wav'.format(username, gs.speaker_name, uttr.name)

            # read wav file to an audio segment
            song = AudioSegment.from_wav(uttr_path)

            # create 1 sec of silence audio segment
            one_sec_segment = AudioSegment.silent(duration=300)  # duration in milliseconds

            # Add above two audio segments
            final_song = song + one_sec_segment

            # Either save modified audio
            tmp_path = 'data/tmp/temp.wav'
            final_song.export(tmp_path, format="wav")



            with open(tmp_path, "rb") as recording_file:
                recording_blob = recording_file.read()


            # with open(uttr_path, "rb") as recording_file:
            #     recording_blob = recording_file.read()
            recording_base64 = base64.b64encode(recording_blob)
            uttr_files['{0}_{1}'.format(gs.speaker_name, uttr.name)] = recording_base64
        json_uttr_file = json.dumps(uttr_files)
        context_dict = {'name': username, 'is_login': True, 'if_choose': if_choose, 'cwd': os.getcwd(), 'gs': gs, 'uttr_files': json_uttr_file}
    return render(request, 'speech/practice.html', context_dict)

@login_required_auth0()
def get_synthesize_status(request):
    if request.method == 'GET':
        username = request.session['profile']['nickname']
        user = User.objects.get(user_name=username)
        slug = request.GET['slug']
        gs = GoldenSpeaker.objects.get(slug=slug, user=user)
        built = gs.status
        name = gs.speaker_name
        json_list = [name, built]
        json_file = json.dumps(json_list)
        return HttpResponse(json_file)



# view to delete golden_speaker
@login_required_auth0()
def delete_golden_speaker(request, speaker_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    gs = GoldenSpeaker.objects.get(slug=speaker_name_slug, user=user)
    if os.path.exists('data/output_wav/{}'.format(gs.speaker_name)):
        files = os.listdir('data/output_wav/{}'.format(gs.speaker_name))
        for f in files:
            os.remove('data/output_wav/{0}/{1}'.format(gs.speaker_name, f))
        os.rmdir('data/output_wav/{}'.format(gs.speaker_name))
    GoldenSpeaker.objects.filter(slug=speaker_name_slug).delete()
    return redirect('/speech/practice/index')


