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

"""This script demos how to run MPD using any input data.

Usage:
    python runtime_mpd_demo.py test.wav test.txt test.TextGrid

Shortcuts for testing:
    CURRENT_PATH=`pwd`
    PROJECT_PATH=${CURRENT_PATH}/../../
    export PYTHONPATH=${PROJECT_PATH}/src:$PYTHONPATH

    python runtime_mpd_demo.py ../../test/data/test_mono_channel.wav \
    ../../test/data/test_mono_channel.txt ../../exp/temp/test.TextGrid

For detailed usage information:
    python runtime_mpd_demo.py -h
"""

import argparse
import os
import time
import ppg
import wavio
from mpd import UtteranceMPD, get_mpd_model_v0, get_mpd_model_v3
from common.feat import read_wav_kaldi_internal
from common import utterance


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform MPD on one '
                                                 'utterance.')
    parser.add_argument('wav_file', metavar='WAV', type=str, nargs='?',
                        help='Path to a wave file.')
    parser.add_argument('text_file', metavar='TEXT', type=str, nargs='?',
                        help='Path to a transcription file.')
    parser.add_argument('tg_file', metavar='TG', type=str, nargs='?',
                        help='Path to the output TextGrid file.')
    args = parser.parse_args()

    # Make sure the input files are valid.
    if not os.path.isfile(args.wav_file):
        raise FileNotFoundError('Wave file %s does not exist.', args.wav_file)
    if not os.path.isfile(args.text_file):
        raise FileNotFoundError('Text file %s does not exist.', args.text_file)

    # Load audio and text data.
    wavio_obj = wavio.read(args.wav_file)
    fs = wavio_obj.rate
    wav = wavio_obj.data
    with open(args.text_file, 'r') as reader:
        text = reader.readline()

    # Demo 1
    # Use the separately-trained fully-connected models.
    # Perform MPD. This method is relatively compact and yet allows some freedom
    # to expose some tunable parameters.
    start_time0 = time.time()
    models_path = get_mpd_model_v0(is_pre_cache=False)
    utt = UtteranceMPD(wav, fs, text)
    utt.prepare_for_mpd(shift=5)
    tg = utt.run_prediction_v0(models_path, threshold=0.32)
    tg.write(args.tg_file+'.v0')
    end_time0 = time.time()
    print('Demo 1: Elapsed time is %2.2f seconds.' % (end_time0-start_time0))

    # Demo 2
    # Use the separately-trained fully-connected models.
    # Perform MPD. This method is more complicated but exposes more tunable
    # parameters. Also, it uses pre-loaded fixtures, so if you are running a
    # lot of jobs that require fast I/O, you should use this method.
    start_time1 = time.time()
    sym_table = utterance.get_hardcoded_sym_table()  # Necessary for MPD feats
    models_cache = get_mpd_model_v0(is_pre_cache=True)  # MPD PyTorch mdls
    utt = UtteranceMPD(wav, fs, text)
    utt.kaldi_shift = 5  # ms
    utt.get_alignment()  # Get forced alignment
    utt.get_phone_tier()  # Set phone tier
    wav_kaldi = read_wav_kaldi_internal(utt.wav, utt.fs)  # To Kaldi format
    ppg_deps = ppg.DependenciesPPG()  # Resources to compute monophone ppgs
    utt.monophone_ppg = ppg.compute_monophone_ppg(wav_kaldi,
                                                  ppg_deps.nnet,
                                                  ppg_deps.lda,
                                                  ppg_deps.monophone_trans,
                                                  utt.kaldi_shift)
    utt.set_hu_feat(sym_table)  # This is the MPD classification feature
    tg = utt.run_prediction_v0(models_cache, threshold=0.32)
    tg.write(args.tg_file+'.v0'+'.fast')
    end_time1 = time.time()
    print('Demo 2: Elapsed time is %2.2f seconds.' % (end_time1 - start_time1))

    # Demo 3
    # Use the joint RNN model.
    # Perform MPD. This method is relatively compact and yet allows some freedom
    # to expose some tunable parameters.
    start_time0 = time.time()
    model = get_mpd_model_v3('../../test/data/model/rnn_joint/mdl.ckpt')
    utt = UtteranceMPD(wav, fs, text)
    utt.prepare_for_mpd(shift=5)
    tg = utt.run_prediction_v3(model, threshold=0.32)
    tg.write(args.tg_file+'.v3')
    end_time0 = time.time()
    print('Demo 3: Elapsed time is %2.2f seconds.' % (end_time0-start_time0))

    # Demo 4
    # Use the joint RNN model.
    # Perform MPD. This method is more complicated but exposes more tunable
    # parameters. Also, it uses pre-loaded fixtures, so if you are running a
    # lot of jobs that require fast I/O, you should use this method.
    start_time1 = time.time()
    sym_table = utterance.get_hardcoded_sym_table()  # Necessary for MPD feats
    model = get_mpd_model_v3('../../test/data/model/rnn_joint/mdl.ckpt')
    utt = UtteranceMPD(wav, fs, text)
    utt.kaldi_shift = 5  # ms
    utt.get_alignment()  # Get forced alignment
    utt.get_phone_tier()  # Set phone tier
    wav_kaldi = read_wav_kaldi_internal(utt.wav, utt.fs)  # To Kaldi format
    ppg_deps = ppg.DependenciesPPG()  # Resources to compute monophone ppgs
    utt.monophone_ppg = ppg.compute_monophone_ppg(wav_kaldi,
                                                  ppg_deps.nnet,
                                                  ppg_deps.lda,
                                                  ppg_deps.monophone_trans,
                                                  utt.kaldi_shift)
    tg = utt.run_prediction_v3(model, threshold=0.32)
    tg.write(args.tg_file+'.v3'+'.fast')
    end_time1 = time.time()
    print('Demo 4: Elapsed time is %2.2f seconds.' % (end_time1 - start_time1))