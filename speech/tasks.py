from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import AnchorSet
import matlab.engine
import os

@shared_task
def build_sabr_model(anchor_set_name_slug, audio_paths, left, right, center, phoneme, pitch_path, output_mat_path):
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug)
    eng = matlab.engine.connect_matlab()
    eng.clear
    eng.addpath('SABR')
    eng.config
    cwd = os.getcwd()
    abs_audio_paths = [cwd + '/' + audio_path + '.wav' for audio_path in audio_paths]
    abs_pitch_path = cwd + '/' + pitch_path
    abs_output_mat_path = cwd + '/' + output_mat_path
    for i, p in enumerate(abs_audio_paths):
        assert os.path.exists(p)
    assert len(left) == len(right)
    assert len(abs_audio_paths) == len(phoneme)
    left = matlab.double(left)
    right = matlab.double(right)
    center = matlab.double(center)
    debug_model = False
    if debug_model:
        abs_output_debug_path = cwd + '/' + 'static/debug'
        eng.service.debug_model(abs_audio_paths, left, right, phoneme, abs_pitch_path, abs_output_debug_path)
    # sucess = eng.build_sabr_model(abs_audio_paths, left, right, phoneme, abs_pitch_path, abs_output_mat_path)
    success = eng.service.build_sabr_model(abs_audio_paths, left, right, phoneme, abs_pitch_path, abs_output_mat_path)
    if success == 1.0:
        anchor_set.built = 'Built'
        anchor_set.save()
    return success

@shared_task
def synthesize_sabr(target_model_name_slug, source_analysis_paths, source_model_path, target_model_path, output_paths):
    cwd = os.getcwd()
    eng = matlab.engine.connect_matlab()
    eng.clear
    eng.addpath(cwd + '/SABR')
    eng.config
    abs_source_analysis_paths = [cwd + '/' + s for s in source_analysis_paths]
    abs_source_model_path = cwd + '/' + source_model_path
    abs_target_model_path = cwd + '/' + target_model_path
    abs_output_paths = [cwd + '/' + o for o in output_paths]
    for p in abs_source_analysis_paths:
        assert os.path.exists(p)
    assert os.path.exists(abs_source_model_path)
    assert os.path.exists(abs_target_model_path)
    success = 1.0
    for i, abs_source_analysis_path in enumerate(abs_source_analysis_paths):
        abs_output_path = abs_output_paths[i]
        suc = eng.service.synthesize(abs_source_analysis_path, abs_source_model_path, abs_target_model_path, abs_output_path)
        if suc == 0.0:
            success = 0.0
    if success == 1.0:
        anchor_set = AnchorSet.objects.get(slug=target_model_name_slug)
        anchor_set.used = True
        anchor_set.save()
    return success