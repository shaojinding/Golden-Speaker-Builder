# Copyright 2019 Guanlong Zhao

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script demos how to run MPD on one single wave file with the joint
LSTM model.

Usage:
    python runtime_mpd_demo_v3_api.py [audio] [transcript] [output]
    python runtime_mpd_demo_v3_api.py test.wav test.txt test.TextGrid

Shortcuts for testing:
    CURRENT_PATH=`pwd`
    PROJECT_PATH=${CURRENT_PATH}/../../
    export PYTHONPATH=${PROJECT_PATH}/src:$PYTHONPATH

    python runtime_mpd_demo_v3_api.py ../../test/data/test_mono_channel.wav \
    ../../test/data/test_mono_channel.txt ../../exp/temp/test.TextGrid

For detailed usage information:
    python runtime_mpd_demo_v3_api.py -h
"""

import argparse
import os
import time
import wavio
from mpd import UtteranceMPD, get_mpd_model_v3

# Static resources.
MPD_MDL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'test/data/model/rnn_joint/mdl.ckpt')


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

    # Use the joint RNN model.
    # Perform MPD. This method is relatively compact and yet allows some freedom
    # to expose some tunable parameters.
    start_time0 = time.time()
    model = get_mpd_model_v3(MPD_MDL_DIR)
    utt = UtteranceMPD(wav, fs, text)
    utt.prepare_for_mpd(shift=5)
    # Different thresholds:
    # threshold=0.33, Precision == Recall = 48.9
    # threshold=0.96761, Precision = 0.71062, Recall = 0.13251
    # All measured on the awareness2018 syllable-level annotations.
    tg = utt.run_prediction_v3(model, threshold=0.96761)
    tg.write(args.tg_file)
    end_time0 = time.time()
    print('Demo 3: Elapsed time is %2.2f seconds.' % (end_time0-start_time0))
