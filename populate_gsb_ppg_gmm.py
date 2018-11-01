import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_project.settings')

import django
import re
django.setup()

from speech.models import SourceModel, Utterance

def populate():
    cbl = add_source_model('cbl')[0]
    gma = add_source_model('gma')[0]
    cache_dir = 'static/ARCTIC'
    week = 'Fall2018'
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
    s = SourceModel.objects.get_or_create(model_name=name)
    return s

# Start execution here!
if __name__ == '__main__':
    print "Starting GSB-PPG population script..."
    populate()