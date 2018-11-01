import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_project.settings')

import django
import re
django.setup()

from speech.models import SourceModel, Utterance

def populate():
    cbl = add_source_model('cbl')
    gma = add_source_model('gma')
    cache_dir = 'static/ARCTIC'
    week = 'Spring2019'
    speakers = {'cbl': cbl, 'gma': gma}
    for speaker in speakers.keys():
        with open('static/ARCTIC/{}/test/prompts.txt'.format(speaker), 'r') as f:
            transcription = f.readlines()
        speaker_files = sorted(os.listdir('{}/{}/test/mat'.format(cache_dir, speaker)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(speaker_files):
            name = f_name.strip().split('.')[0]
            trans = transcription[i].strip()
            add_uttr(name, speakers[speaker], trans, week)

def add_uttr(name, source_model, trans, week):
    u = Utterance.objects.get_or_create(name=name, source_model=source_model, transcription=trans, week=week)
    return u

def add_source_model(name):
    s = SourceModel.objects.get_or_create(model_name=name)[0]
    cache_dir = 'static/ARCTIC'
    cached_files = sorted(os.listdir('{}/{}/train/mat'.format(cache_dir, name)), key=lambda x: (int(re.sub('\D', '', x)), x))
    cached_file_paths = [os.path.join('{}/{}/train/mat'.format(cache_dir, name), c) for c in cached_files]
    s.set_cached_file_paths(cached_file_paths)
    s.pitch_model_dir = '{}/{}/pitch_model/model.mat'.format(cache_dir, name)
    s.save()
    return s

# Start execution here!
if __name__ == '__main__':
    print "Starting GSB-PPG population script..."
    populate()