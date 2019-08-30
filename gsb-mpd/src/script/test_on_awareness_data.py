# Copyright 2018 Guanlong Zhao

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script tests the MPD system on the awareness study annotations."""

import os
import time
import ppg
import wavio
import numpy as np
import matplotlib.pyplot as plt
from mpd import UtteranceMPD, get_mpd_model_v0, get_mpd_model_v1,\
    get_mpd_model_v2, get_mpd_model_v3
from common.feat import read_wav_kaldi_internal
from common import utterance, align
from simple_word import Word
import xmltodict
import pandas
from copy import deepcopy
from math import isnan
from sklearn.metrics import precision_recall_curve
import scipy


if __name__ == '__main__':
    # Settings
    # 'fc_separate' | 'fc_joint' | 'rnn_separate' | 'rnn_joint'
    model_type = 'fc_separate'
    exp_codename = '2999_train_max_syllable' + '_' + model_type + '_2-layer'
    exp_description = """Using the phoneme-dependent MPD models, training set
    has 2999 utts, and pick the max scores over all phonemes in a syllable 
    as the syllable level score. Each using a 2-layer classifier."""
    model_path = '/home/guanlong/PycharmProjects/gsb-mpd/exp/' \
                 'separated_classifiers_20181130-195115'  # 'fc_separate'
    #             'joint_classifiers_2018124-153513/mdl.ckpt'  # 'rnn_joint'
    #             'joint_classifiers_2018124-15218/mdl.ckpt'  # 'fc_joint'
    #             'separated_classifiers_20181204-142703'  # 'rnn_separate'
    visualization_threshold = 0.27
    is_test = False
    is_use_cache = True  # Use cache from previous runs or not.
    awareness_root = '/data_repo/awareness2018'
    resources_dir = os.path.join(awareness_root, 'resources')
    audio_dir = os.path.join(awareness_root, 'audio')
    if is_test:
        exp_codename = 'test'
        cache_dir = os.path.join(awareness_root, 'cache_test')
    else:
        cache_dir = os.path.join(awareness_root, 'cache')
    exp_dir = os.path.join(awareness_root, 'exp')
    curr_output_dir = os.path.join(exp_dir, exp_codename)
    if not os.path.isdir(curr_output_dir):
        os.mkdir(curr_output_dir)
    curr_tg_dir = os.path.join(curr_output_dir, 'tg')
    if not os.path.isdir(curr_tg_dir):
        os.mkdir(curr_tg_dir)

    # Prepare data for scoring.
    words = {}
    with open(os.path.join(resources_dir, 'dict_syllable'), 'r') as reader:
        for each_line in reader:
            parse_line = each_line[0:-1].split('  ')
            word = Word(parse_line[0], parse_line[1])
            words[word.symbol] = word

    syllable_split = {}
    with open(os.path.join(resources_dir, 'syllables.xml'), 'r') as reader:
        parse_s = xmltodict.parse(reader.read())
    for each_sentence in parse_s['root']['sentence']:
        sentence_id = int(each_sentence['@id'])
        syllables = []
        for each_syllable in each_sentence['syllable']:
            syllables.append((int(each_syllable['@id']),
                              each_syllable['#text']))
        syllable_split[sentence_id] = syllables

    sentences = {}
    sentences_in_full_text = {}
    with open(os.path.join(resources_dir, 'prompts'), 'r') as reader:
        for each_line in reader:
            parse_line = each_line[0:-1].split('|')
            sentence_id = int(parse_line[0])
            curr_words = []
            for each_word in parse_line[1].split():
                curr_words.append(deepcopy(words[each_word.upper()]))
            sentences[sentence_id] = curr_words
            sentences_in_full_text[sentence_id] = parse_line[1]

    sentences_in_index = deepcopy(sentences)
    for key, val in sentences_in_index.items():
        syllable_idx = syllable_split[key]
        syllable_counter = 0
        phoneme_counter = 0
        for each_word in val:
            for each_syllable in each_word.syllable:
                assert each_syllable.symbol == syllable_idx[
                    syllable_counter][1].upper()
                each_syllable.symbol = syllable_idx[syllable_counter][0]
                syllable_counter += 1
                for each_phoneme in each_syllable.pronunciation:
                    each_phoneme.symbol = phoneme_counter
                    phoneme_counter += 1

    answers = {}
    df = pandas.read_excel(os.path.join(resources_dir,
                                        'annotations.xlsx'), 'annotations')
    for index, row in df.iterrows():
        sentence_id = row['SENTENCE_ID']
        subject_id = row['SUBJECT_ID']
        true_errors = row['TRUE_ANNOTATION']
        if isinstance(true_errors, float) and isnan(true_errors):
            true_errors = ''
        if true_errors:
            true_errors = [int(val) for val in str(true_errors).split(',')]
        else:
            true_errors = []
        answers[(sentence_id, subject_id)] = [1 if val[0] in true_errors else 0
                                              for val in
                                              syllable_split[sentence_id]]

    # Prepare fixtures.
    sym_table = utterance.get_hardcoded_sym_table()  # Necessary for MPD feats
    # MPD PyTorch models
    if model_type == 'fc_separate':
        models_cache = get_mpd_model_v0(is_pre_cache=True,
                                        model_root=model_path)
    elif model_type == 'fc_joint':
        models_cache = get_mpd_model_v1(model_path)
    elif model_type == 'rnn_separate':
        models_cache = get_mpd_model_v2(model_path)
    elif model_type == 'rnn_joint':
        models_cache = get_mpd_model_v3(model_path)
    else:
        raise ValueError('Model type %s not supported!', model_type)
    ppg_deps = ppg.DependenciesPPG()  # Resources to compute monophone ppgs
    aligner = align.MontrealAligner(
        dict_path=os.path.join(resources_dir, 'dict'))

    # Scoring
    raw_scores = []
    all_answers = []
    time_spent = []
    num_utts = len(answers)
    processed = 0
    for key, val in answers.items():
        start_time = time.time()
        if is_test:
            # Debug
            if processed == 3:
                break
        all_answers.extend(val)

        sentence_id = key[0]
        speaker_id = key[1]

        cache_file = os.path.join(cache_dir,
                                  '%s_%d.proto' % (speaker_id, sentence_id))

        if is_use_cache and os.path.isfile(cache_file):
            print('Using cache file.')
            utt = UtteranceMPD()
            utt.read(cache_file)
        else:
            wav_file = os.path.join(audio_dir,
                                    '%s_%d.wav' % (speaker_id, sentence_id))
            text = sentences_in_full_text[sentence_id]

            wavio_obj = wavio.read(wav_file)
            fs = wavio_obj.rate
            wav = wavio_obj.data

            utt = UtteranceMPD(wav, fs, text)
            utt.kaldi_shift = 5  # ms
            # Get forced alignment
            tg = aligner.align_single_internal(utt.wav, utt.fs, utt.text)
            utt.align = tg

            utt.get_phone_tier()  # Set phone tier
            # To Kaldi format
            wav_kaldi = read_wav_kaldi_internal(utt.wav, utt.fs)
            utt.monophone_ppg = ppg.compute_monophone_ppg(
                wav_kaldi, ppg_deps.nnet, ppg_deps.lda,
                ppg_deps.monophone_trans, utt.kaldi_shift)
        if model_type == 'fc_separate':
            tg = utt.run_prediction_v0(models_cache,
                                       threshold=visualization_threshold)
        elif model_type == 'fc_joint':
            tg = utt.run_prediction_v1(models_cache,
                                       threshold=visualization_threshold)
        elif model_type == 'rnn_separate':
            tg = utt.run_prediction_v2(models_cache,
                                       threshold=visualization_threshold)
        elif model_type == 'rnn_joint':
            tg = utt.run_prediction_v3(models_cache,
                                       threshold=visualization_threshold)
        else:
            raise ValueError('Model type %s not supported!', model_type)

        filtered_scores = []
        for i, each_phone in enumerate(utt.phone):
            if not utterance.is_sil(each_phone.mark):
                filtered_scores.append(utt.score[i])

        # Convert phoneme level scores to syllable level
        sentence_to_syllable = sentences_in_index[sentence_id]
        for each_word in sentence_to_syllable:
            for each_syllable in each_word.syllable:
                phoneme_idx = [val.symbol
                               for val in each_syllable.pronunciation]
                raw_scores.append(
                    np.max([filtered_scores[ii] for ii in phoneme_idx]))

        assert len(all_answers) == len(raw_scores), 'Mismatch!'
        end_time = time.time()
        duration = end_time - start_time
        time_spent.append(duration)
        print('Took %1.2f seconds.' % duration)
        processed += 1
        print('Processed %3.2f%%.' % (100 * processed / num_utts))

        # Cache data.
        utt.write(cache_file)
        tg_file = os.path.join(curr_tg_dir,
                               '%s_%d.TextGrid' % (speaker_id, sentence_id))
        tg.write(tg_file)

    precision, recall, thresholds = precision_recall_curve(
        all_answers, raw_scores)

    # Get F1 score when precision==recall.
    diff = abs(precision - recall)
    idx = diff.argmin()
    f1 = 100 * 2 * precision[idx] * recall[idx] / (precision[idx] + recall[idx])
    print('F1 is %2.1f' % f1)
    print('Threshold is %1.2f' % thresholds[idx])
    plt.plot(precision, recall)
    plt.xlabel('Precision')
    plt.ylabel('Recall')
    print('Saving precision-recall curve...')
    plt.savefig(os.path.join(curr_output_dir, 'pr_curve.pdf'), dpi=600)
    average_time = sum(time_spent) / num_utts
    print('Average processing time per utterance is %1.2f seconds.' %
          average_time)
    print('Saving analysis data to a mat file...')
    scipy.io.savemat(os.path.join(curr_output_dir, 'analysis.mat'),
                     {'predicts': raw_scores, 'answers': all_answers,
                      'precision': precision, 'recall': recall,
                      'threshold': thresholds, 'f1': f1, 'f1_idx': idx,
                      'processing_time': time_spent,
                      'average_time': average_time})

    # Save settings
    with open(os.path.join(curr_output_dir, 'README'), 'w') as writer:
        writer.write('F1 is %2.1f\n' % f1)
        writer.write('Threshold is %1.2f\n\n' % thresholds[idx])
        writer.write('Average time = %1.2f\n' % average_time)
        writer.write('Model type = %s\n' % model_type)
        writer.write('Exp code name = %s\n' % exp_codename)
        writer.write('Exp description = %s\n' % exp_description)
        writer.write('TG visualization threshold = %1.2f\n'
                     % visualization_threshold)
        model_path = model_path if model_path else 'default'
        writer.write('MPD models root path = %s\n' % model_path)
        writer.write('is_use_cache = %d\n' % is_use_cache)
        writer.write('is_test = %d\n' % is_test)
