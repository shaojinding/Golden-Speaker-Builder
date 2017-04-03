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
    week_dir = os.listdir('static/ARCTIC/cache')
    for week in week_dir:
        bdl_files = sorted(os.listdir('static/ARCTIC/cache/{}/bdl'.format(week)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(bdl_files):
            name = f_name.strip().split('.')[0]
            for t in transcription:
                if name in t.strip():
                    trans = t.strip()[16: -3]
                    add_uttr(name, bdl, trans, week)
                    break
        clb_files = sorted(os.listdir('static/ARCTIC/cache/{}/clb'.format(week)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(clb_files):
            name = f_name.strip().split('.')[0]
            for t in transcription:
                if name in t.strip():
                    trans = t.strip()[16: -3]
                    add_uttr(name, bdl, trans, week)
                    break
        rms_files = sorted(os.listdir('static/ARCTIC/cache/{}/rms'.format(week)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(rms_files):
            name = f_name.strip().split('.')[0]
            for t in transcription:
                if name in t.strip():
                    trans = t.strip()[16: -3]
                    add_uttr(name, bdl, trans, week)
                    break
        slt_files = sorted(os.listdir('static/ARCTIC/cache/{}/slt'.format(week)), key=lambda x: (int(re.sub('\D', '', x)), x))
        for i, f_name in enumerate(slt_files):
            name = f_name.strip().split('.')[0]
            for t in transcription:
                if name in t.strip():
                    trans = t.strip()[16: -3]
                    add_uttr(name, bdl, trans, week)
                    break

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