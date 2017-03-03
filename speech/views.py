import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django_auth0.auth_decorator import login_required_auth0
from django.views.decorators.csrf import ensure_csrf_cookie
from models import User, Recording, AnchorSet, Anchor, SourceModel, Utterance, GoldenSpeaker
from .forms import AnchorSetForm
from time import gmtime, strftime, time
from django.contrib import messages
import base64
import json
from tasks import build_sabr_model, synthesize_sabr


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
    anchorset_list = AnchorSet.objects.filter(user=user)
    building_anchor_set = []
    for anchorset in anchorset_list:
        if anchorset.built == 'In processing':
            building_anchor_set.append(anchorset.slug)
    json_building_anchor_set = json.dumps(building_anchor_set)
    context_dict = {'anchorsets': anchorset_list, 'name': username, 'is_login': True,
                    'building_anchor_set': json_building_anchor_set}
    return render(request, 'speech/manage_anchorset.html', context_dict)


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
            anchorset = anchorset_form.save(commit=False)
            anchorset.active = False
            anchorset.used = False
            anchorset.completed = False
            anchorset.built = "False"
            anchorset.user = user
            anchorset.timestamp = strftime("%b %d %Y %H:%M:%S", gmtime())
            anchorset.set_saved_phonemes([])
            anchorset.save()
            anchorset.sabr_model_path = 'static/sabr/{}.mat'.format(anchorset.slug)
            anchorset.pitch_path = 'static/pitch/{}.wav'.format(anchorset.slug)
            anchorset.save()
            return redirect('/speech/start_record_session/{}'.format(anchorset.slug))
        else:
            print anchorset_form.errors
    else:
        anchorset_form = AnchorSetForm()
    context_dict = {'anchorset_form': anchorset_form, 'name': username, 'is_login': True}
    return render(request, 'speech/add_anchorset.html', context_dict)


# delete anchor set operation view
@login_required_auth0()
def delete_anchorset(request, anchor_set_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if 'current_anchorset' in request.session:
        if request.session['current_anchorset'] == anchor_set_name_slug:
            del request.session['current_anchorset']
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
    completed = anchor_set.completed
    with open('static/doc/keywords.txt', 'r') as kw_f:
        lines = kw_f.readlines()
    ipas = []
    keywords = []
    for line in lines:
        items = line.strip().split(' ')
        ipas.append(items[0])
        keywords.append(items[1])
    json_ipas = json.dumps(ipas)
    json_keywords = json.dumps(keywords)

    if phoneme in saved_phonemes:
        anchor = Anchor.objects.get(anchor_set=anchor_set, phoneme=phoneme)
        recording = anchor.recording
        record_name = recording.record_name
        with open("static/recordings/%s.wav" % record_name, "rb") as recording_file:
            recording_blob = recording_file.read()
        recording_base64 = base64.b64encode(recording_blob)
        json_record_details = json.dumps([anchor.L, anchor.R, anchor.C, recording_base64])
        context_dict = {'name': username, 'is_login': True,
                        'phoneme': phoneme, 'record_details': json_record_details,
                        'saved_phoneme': json_saved_phoneme, 'completed': completed,
                        'ipas': json_ipas, 'keywords': json_keywords}
    else:
        context_dict = {'name': username, 'is_login': True,
                        'phoneme': phoneme, 'record_details': "[]",
                        'saved_phoneme': json_saved_phoneme, 'completed': completed,
                        'ipas': json_ipas, 'keywords': json_keywords}
    return render(request, 'speech/record.html', context_dict)


# anchor set recording finished, pitch recording page
@login_required_auth0()
def finish_record_session(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set_name_slug = request.session['current_anchorset']
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    num_phoneme = 39
    if len(anchor_set.get_saved_phonemes()) >= num_phoneme:
        # del request.session['current_anchorset']
        anchor_set.completed = True
        anchor_set.save()
    else:
        messages.add_message(request, messages.INFO,
                             'You did not finish recording '
                             'all anchor sets, please finish them first.')
        return redirect('/speech/record/index')
    pitch_path = anchor_set.pitch_path
    with open('static/doc/pitch.txt', 'r') as pitch_f:
        pitch_doc = pitch_f.readline()
    if os.path.exists(pitch_path):
        with open(pitch_path, "rb") as recording_file:
            recording_blob = recording_file.read()
        recording_base64 = base64.b64encode(recording_blob)
        context_dict = {'anchor_set_name': anchor_set.anchor_set_name, 'name': username, 'is_login': True,
                        'pitch_file': recording_base64, 'pitch_doc': pitch_doc}
    else:
        context_dict = {'anchor_set_name': anchor_set.anchor_set_name, 'name': username, 'is_login': True,
                        'pitch_file': None, 'pitch_doc': pitch_doc}

    return render(request, 'speech/finish_record.html', context_dict)


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
            current_anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
            saved_phonemes = current_anchorset.get_saved_phonemes()
            if phoneme in saved_phonemes:
                anc = Anchor.objects.get(anchor_set=current_anchorset, phoneme=phoneme)
                anc.L = L
                anc.R = R
                anc.C = C
                anc.save()
                if re_record:
                    recording_base64 = request.POST['recording']
                    recording_blob = base64.b64decode(recording_base64)
                    rec = anc.recording
                    record_name = rec.record_name
                    with open("static/recordings/%s.wav" % record_name, "wb") as recording_file:
                        recording_file.write(recording_blob)
            else:
                recording_base64 = request.POST['recording']
                saved_phonemes.append(phoneme)
                request.session['saved_phonemes'] = saved_phonemes
                current_anchorset.set_saved_phonemes(saved_phonemes)
                current_anchorset.save()
                record_name = str(Recording.objects.count())
                recording_blob = base64.b64decode(recording_base64)
                with open("static/recordings/%s.wav" % record_name, "wb") as recording_file:
                    recording_file.write(recording_blob)
                rec = Recording(record_name=record_name, phoneme=phoneme, user=user)
                rec.save()
                anc = Anchor(recording=rec, anchor_set=current_anchorset, phoneme=phoneme, L=L, R=R, C=C)
                anc.save()
    return HttpResponse('sucess')


# view for uploading pitch
@login_required_auth0()
@ensure_csrf_cookie
def upload_pitch(request):
    if request.method == 'POST':
        username = request.session['profile']['nickname']
        user = User.objects.get(user_name=username)
        anchor_set_name_slug = request.session['current_anchorset']
        current_anchorset = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
        pitch_path = current_anchorset.pitch_path
        pitch_base64 = request.POST['recording']
        pitch_blob = base64.b64decode(pitch_base64)
        with open(pitch_path, "wb") as recording_file:
            recording_file.write(pitch_blob)
    return HttpResponse('sucess')


# view for building sabr model
@login_required_auth0()
def build_sabr(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    anchor_set_name_slug = request.session['current_anchorset']
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    if anchor_set.built == 'Built':
        return redirect('/speech')
    anchor_set.built = 'In processing'
    anchor_set.save()
    anchors = Anchor.objects.filter(anchor_set=anchor_set).order_by('phoneme')
    audio_paths = []
    left = []
    right = []
    center = []
    phoneme = []
    pitch_path = anchor_set.pitch_path
    output_mat_path = anchor_set.sabr_model_path
    for anchor in anchors:
        recording = anchor.recording
        audio_paths.append('static/recordings/{}'.format(recording.record_name))
        phoneme.append(str(recording.phoneme))
        left.append(anchor.L)
        right.append(anchor.R)
        center.append(anchor.C)
    build_sabr_model.delay(username, anchor_set_name_slug, audio_paths, left, right, center,
                                    phoneme, pitch_path, output_mat_path)
    return redirect('/speech')


# page to choose source and target anchor set, and choose utterance to be built
@login_required_auth0()
def build_synthesize(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    source_models = SourceModel.objects.all()
    anchor_sets = AnchorSet.objects.filter(user=user, built='Built')
    utterances = Utterance.objects.all()
    context_dict = {'name': username, 'is_login': True, 'source_models': source_models,
                    'anchor_sets': anchor_sets, 'utterances': utterances}
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
        json_list = [names, trans]
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
        name = anchorset.anchor_set_name
        json_list = [name, built]
        json_file = json.dumps(json_list)
        return HttpResponse(json_file)


# view for synthesize
@login_required_auth0()
def synthesize(request):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if request.method == 'POST':
        select_names_string = request.POST['select_names']
        source_model_name = request.POST['source_model']
        target_model_name = request.POST['target_model']
        if select_names_string and source_model_name and target_model_name:
            select_names = select_names_string.strip().split(',')
            source_model = SourceModel.objects.get(model_name=source_model_name)
            target_model = AnchorSet.objects.get(anchor_set_name=target_model_name)
            target_model_name_slug = target_model.slug
            timestamp = str(time())
            gs_name = source_model_name + '-' + target_model_name + '-' + timestamp.replace('.', '-')
            gs = GoldenSpeaker(speaker_name=gs_name, source_model=source_model, anchor_set=target_model,
                               user=user, timestamp=strftime("%b %d %Y %H:%M:%S", gmtime()), status="Synthesizing")
            gs.save()
            for name in select_names:
                uttr = Utterance.objects.get(name=name, source_model=source_model)
                gs.contained_utterance.add(uttr)
            gs.save()
            slug = gs.slug
            output_wav_folder = 'static/output_wav/' + slug
            if not os.path.exists(output_wav_folder):
                os.mkdir(output_wav_folder)
            output_wav_path = [output_wav_folder + '/' + u + '.wav' for u in select_names]
            source_model_path = 'static/ARCTIC/models/' + source_model_name + '.mat'
            target_model_path = 'static/sabr/' + target_model_name + '.mat'
            utterance_path = ['static/ARCTIC/cache/' + source_model_name + '/' + u + '.mat' for u in select_names]
            synthesize_sabr.delay(username, gs_name, target_model_name_slug, utterance_path, source_model_path, target_model_path, output_wav_path)
            # synthesize_sabr(utterance_path, source_model_path, target_model_path, output_wav_path)
    return redirect('/speech/practice/index')


# view for practice
@login_required_auth0()
def practice(request, golden_speaker_name_slug):
    username = request.session['profile']['nickname']
    user = User.objects.get(user_name=username)
    if golden_speaker_name_slug == 'index':
        if_choose = True
        gss = GoldenSpeaker.objects.order_by('-timestamp').filter(user=user)
        building_gs = []
        for gs in gss:
            if gs.status == 'Synthesizing':
                building_gs.append(gs.slug)
        json_building_gs = json.dumps(building_gs)
        context_dict = {'name': username, 'is_login': True, 'if_choose': if_choose, 'golden_speakers': gss, 'building_golden_speakers': json_building_gs}
    else:
        if_choose = False
        gs = GoldenSpeaker.objects.get(slug=golden_speaker_name_slug)
        context_dict = {'name': username, 'is_login': True, 'if_choose': if_choose, 'cwd': os.getcwd(), 'gs': gs}
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
    GoldenSpeaker.objects.filter(slug=speaker_name_slug).delete()
    return redirect('/speech/practice/index')