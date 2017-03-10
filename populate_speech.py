import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_project.settings')

import django
import re
django.setup()

from speech.models import SourceModel, Utterance


def populate():
    bdl = add_source_model('bdl')[0]
    clb = add_source_model('clb')[0]
    rms = add_source_model('rms')[0]
    slt = add_source_model('slt')[0]
    with open('static/ARCTIC/transcription/cmuarctic.data', 'r') as f:
        transcription = f.readlines()
    bdl_files = sorted(os.listdir('static/ARCTIC/cache/bdl'), key=lambda x: (int(re.sub('\D', '', x)), x))
    for i, f_name in enumerate(bdl_files):
        name = f_name.strip().split('.')[0]
        trans = transcription[i].strip()[16: -3]
        add_uttr(name, bdl, trans)
    clb_files = sorted(os.listdir('static/ARCTIC/cache/clb'), key=lambda x: (int(re.sub('\D', '', x)), x))
    for i, f_name in enumerate(clb_files):
        name = f_name.strip().split('.')[0]
        trans = transcription[i].strip()[16: -3]
        add_uttr(name, clb, trans)
    rms_files = sorted(os.listdir('static/ARCTIC/cache/rms'), key=lambda x: (int(re.sub('\D', '', x)), x))
    for i, f_name in enumerate(rms_files):
        name = f_name.strip().split('.')[0]
        trans = transcription[i].strip()[16: -3]
        add_uttr(name, rms, trans)
    slt_files = sorted(os.listdir('static/ARCTIC/cache/slt'), key=lambda x: (int(re.sub('\D', '', x)), x))
    for i, f_name in enumerate(slt_files):
        name = f_name.strip().split('.')[0]
        trans = transcription[i].strip()[16: -3]
        add_uttr(name, slt, trans)

def add_uttr(name, source_model, trans):
    u = Utterance.objects.get_or_create(name=name, source_model=source_model, transcription=trans)
    return u

def add_source_model(name):
    s = SourceModel.objects.get_or_create(model_name=name)
    return s

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()