from __future__ import absolute_import, unicode_literals
from celery import shared_task
from speech.models import AnchorSet, User, GoldenSpeaker
import matlab.engine
import os
import logging


@shared_task
def data_preprocess(username, anchor_set_name_slug, audio_paths, left, right, output_mat_path, pitch_model_path):
    assert_success = False
    matlab_success = False
    text_path = 'static/doc/sentences.txt'
    matlab_dependency_script_path = '../gzhao/vc-tools/script'
    user = User.objects.get(user_name=username)
    cwd = os.getcwd()
    text_path = os.path.join(cwd, text_path)
    abs_audio_paths = [os.path.join(cwd, audio_path) for audio_path in audio_paths]
    try:
        for i, p in enumerate(abs_audio_paths):
            assert os.path.exists(p)
        assert len(left) == len(right)
        assert_success = True
    except:
        logging.exception('Errors in path assert')
    left = matlab.double(left)
    right = matlab.double(right)
    abs_output_mat_path = os.path.join(cwd, output_mat_path)
    abs_pitch_model_path = os.path.join(cwd, pitch_model_path)

    try:
        eng = matlab.engine.start_matlab()
        eng.clear(nargout=0)
        eng.addpath(matlab_dependency_script_path)
        eng.addDependencies(nargout=0)
        # debug_model = False
        # if debug_model:
        #     abs_output_debug_path = cwd + '/' + 'static/debug'
        #     eng.cd(cwd)
        #     eng.debug_model(abs_audio_paths, left, right, phoneme, abs_pitch_path, abs_output_debug_path)
        cached_file_paths = eng.dataPrep(abs_audio_paths, text_path, abs_output_mat_path, 'StartTime', left,
                                         'EndTime', right, 'NumWorkers', 4)
        eng.buildPitchModelGSB(cached_file_paths, abs_pitch_model_path)
        eng.quit()
        matlab_success = True
    except:
        eng.quit()
        logging.exception('Errors during in MATLAB process')
    anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
    if assert_success and matlab_success:
        anchor_set.set_cached_file_paths(cached_file_paths)
        anchor_set.built = 'Built'
    else:
        anchor_set.built = 'Error'
    anchor_set.save()

# @shared_task
# def build_pitch_model(username, anchor_set_name_slug, utt_paths, model_path):
#     matlab_dependency_script_path = '../gzhao/vc-tools/script'
#     user = User.objects.get(user_name=username)
#     cwd = os.getcwd()
#     abs_utt_paths = [os.path.join(cwd, utt_path) for utt_path in utt_paths]
#     for i, p in enumerate(abs_utt_paths):
#         assert os.path.exists(p)
#     abs_model_path = os.path.join(cwd, model_path)
#     try:
#         eng = matlab.engine.start_matlab()
#         eng.clear(nargout=0)
#         eng.addpath(matlab_dependency_script_path)
#         eng.addDependencies(nargout=0)
#         eng.buildPitchModelGSB(abs_utt_paths, abs_model_path)
#         anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
#         anchor_set.pitch_model_built = 'Built'
#         anchor_set.save()
#     except:
#         logging.exception('')
#         anchor_set = AnchorSet.objects.get(slug=anchor_set_name_slug, user=user)
#         anchor_set.pitch_model_built = 'Error'
#         anchor_set.save()


# @shared_task
# def build_gmm_model(username, gs_name, source_utt_paths, target_utt_paths, gmm_model_path):
#     matlab_dependency_script_path = '../gzhao/vc-tools/script'
#     user = User.objects.get(user_name=username)
#     cwd = os.getcwd()
#     abs_source_utt_paths = [os.path.join(cwd, src_utt_path) for src_utt_path in source_utt_paths]
#     abs_target_utt_paths = [os.path.join(cwd, tgt_utt_path) for tgt_utt_path in target_utt_paths]
#     abs_gmm_model_path = os.path.join(cwd, gmm_model_path)
#     for p in abs_source_utt_paths:
#         assert os.path.exists(p)
#     for p in abs_target_utt_paths:
#         assert os.path.exists(p)
#     success = False
#     try:
#         eng = matlab.engine.start_matlab()
#         eng.clear(nargout=0)
#         eng.addpath(matlab_dependency_script_path)
#         eng.build_gmm_model(abs_source_utt_paths, abs_target_utt_paths, abs_gmm_model_path)
#         eng.quit()
#         success = True
#     except:
#         logging.exception('Errors during in MATLAB process')
#     gs = GoldenSpeaker.objects.get(user=user, speaker_name=gs_name)
#     if success:
#         gs.status = "Finished"
#     else:
#         gs.status = "Error"
#     gs.save()

@shared_task
def gmm_synthesize(username, gs_name, utt_paths, gmm_model_path, source_utt_paths, target_utt_paths,
               src_pitch_model_path, tgt_pitch_model_path, output_wav_folder):
    assert_success = False
    matlab_success = False
    matlab_dependency_script_path = '../gzhao/vc-tools/script'
    user = User.objects.get(user_name=username)
    cwd = os.getcwd()
    abs_source_utt_paths = [os.path.join(cwd, src_utt_path) for src_utt_path in source_utt_paths]
    abs_target_utt_paths = [os.path.join(cwd, tgt_utt_path) for tgt_utt_path in target_utt_paths]
    abs_gmm_model_path = os.path.join(cwd, gmm_model_path)
    abs_utt_paths = [os.path.join(cwd, utt_path) for utt_path in utt_paths]
    abs_src_pitch_model_path = os.path.join(cwd, src_pitch_model_path)
    abs_tgt_pitch_model_path = os.path.join(cwd, tgt_pitch_model_path)
    abs_output_wav_folder = os.path.join(cwd, output_wav_folder)
    try:
        for p in abs_source_utt_paths:
            assert os.path.exists(p)
        for p in abs_target_utt_paths:
            assert os.path.exists(p)
        for p in abs_utt_paths:
            assert os.path.exists(p)
        assert os.path.exists(abs_src_pitch_model_path)
        assert os.path.exists(abs_tgt_pitch_model_path)
        assert_success = True
    except:
        logging.exception('Errors in path assert')

    try:
        eng = matlab.engine.start_matlab()
        eng.clear(nargout=0)
        eng.addpath(matlab_dependency_script_path)
        eng.addDependencies(nargout=0)
        if not os.path.exists(abs_gmm_model_path):
            eng.buildGMMmodelGSB(abs_source_utt_paths, abs_target_utt_paths, abs_gmm_model_path)
        eng.voiceConversionInterfaceGSB(abs_utt_paths, abs_gmm_model_path, abs_src_pitch_model_path,
                                                  abs_tgt_pitch_model_path, abs_output_wav_folder,
                                        'NumWorkers', 4)
        eng.quit()
        matlab_success = True
    except:
        logging.exception('Errors during in MATLAB process')
        eng.quit()
    gs = GoldenSpeaker.objects.get(user=user, speaker_name=gs_name)
    if assert_success and matlab_success:
        gs.status = "Finished"
    else:
        gs.status = "Error"
    gs.save()
