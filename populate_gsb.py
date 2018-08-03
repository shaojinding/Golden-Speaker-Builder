import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_project.settings')

import django
import re
django.setup()

from speech.models import SourceModel, Utterance


# def populate():
#     bda = add_source_model('bda')[0]
#     jba = add_source_model('jba')[0]
#     kpa = add_source_model('kpa')[0]
#     rza = add_source_model('rza')[0]
#     cache_dir = 'static/ARCTIC/cache'
#     week = 'Fall2017'
#     with open('static/ARCTIC/transcription/ns_prompts.txt', 'r') as f:
#         transcription = f.readlines()
#     speakers = {'bda': bda, 'jba': jba, 'kpa': kpa, 'rza': rza}
#     for speaker in speakers.keys():
#         speaker_files = sorted(os.listdir('{}/{}/{}'.format(cache_dir, week, speaker)), key=lambda x: (int(re.sub('\D', '', x)), x))
#         for i, f_name in enumerate(speaker_files):
#             name = f_name.strip().split('.')[0]
#             trans = transcription[300 + i].strip()
#             add_uttr(name, speakers[speaker], trans, week)

def populate():
    cbl = add_source_model('cbl')[0]
    gma = add_source_model('gma')[0]
    cache_dir = 'static/ARCTIC/cache'
    week = 'Fall2017'
    with open('static/ARCTIC/transcription/ns_prompts.txt', 'r') as f:
        transcription = f.readlines()
    speakers = {'cbl': cbl, 'gma': gma}
    for speaker in speakers.keys():
        speaker_files = sorted(os.listdir('{}/{}/{}'.format(cache_dir, week, speaker)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(speaker_files):
            name = f_name.strip().split('.')[0]
            trans = transcription[300 + i].strip()
            add_uttr(name, speakers[speaker], trans, week)

def add_uttr(name, source_model, trans, week):
    u = Utterance.objects.get_or_create(name=name, source_model=source_model, transcription=trans, week=week)
    return u

def add_source_model(name):
    s = SourceModel.objects.get_or_create(model_name=name)
    return s

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()