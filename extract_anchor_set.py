import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_project.settings')
import django

django.setup()
from speech.models import AnchorSet, Anchor
import scipy.io as sio
import numpy as np

def extract_anchor_set(anchor_set_name, save_dir):
    anchor_set = AnchorSet.objects.get(anchor_set_name=anchor_set_name)
    anchors = Anchor.objects.filter(anchor_set=anchor_set)
    # info = np.zeros((39, 3))
    info = []
    for i, anchor in enumerate(anchors):
        # info[i, :] = [anchor.recording.record_name, anchor.L, anchor.C, anchor.R]
        info.append([int(anchor.recording.record_name), anchor.L, anchor.C, anchor.R])
    sio.savemat(save_dir, {'info': info})

if __name__ == '__main__':
    extract_anchor_set('evgeny1', '/home/shaojinding/Project/gs_data/evgeny/info/info.mat')