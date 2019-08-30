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

"""This script processes data utterances for the MPD task."""

import os
import logging
import time
from glob import glob
from mpd import UtteranceMPD
from common.feat import read_wav_kaldi_internal
from ppg import DependenciesPPG, compute_monophone_ppg
import wavio
from common import utterance
from textgrid import TextGrid


def process_utt(wav, fs, text, tg, ppg_deps):
    """Generate data utterance for one sentence.

    Args:
        wav: Speech data in ndarray.
        fs: Sampling frequency.
        text: Transcript.
        tg: Textgrid object.
        ppg_deps: Dependencies for computing the PPGs.

    Returns:
        utt: The data utterance.
    """
    utt = UtteranceMPD(wav, fs, text)
    utt.align = tg
    utt.kaldi_shift = 5  # ms
    wav_kaldi = read_wav_kaldi_internal(wav, fs)
    utt.monophone_ppg = compute_monophone_ppg(wav_kaldi, ppg_deps.nnet,
                                              ppg_deps.lda,
                                              ppg_deps.monophone_trans,
                                              utt.kaldi_shift)
    phone_tier = utterance.time_to_frame_interval_tier(tg.getFirst('phones'),
                                                       utt.kaldi_shift)
    phone_tier = utterance.normalize_tier_mark(phone_tier)
    utt.phone = phone_tier
    word_tier = utterance.time_to_frame_interval_tier(tg.getFirst('words'),
                                                      utt.kaldi_shift)
    word_tier = utterance.normalize_tier_mark(word_tier, 'NormalizeWord')
    utt.word = word_tier
    return utt


def process_speaker(path, gender='', dialect='', skip_exist=True):
    """Process data for one speaker.

    Args:
        path: Root dir to that speaker.
        gender: [optional] Gender.
        dialect: [optional] Dialect.
        skip_exist: [optional] If True then skip files that have already cached.
    """
    if not os.path.isdir(path):
        logging.error('Path %s does not exist.', path)
    speaker_id = os.path.basename(path)
    wav_dir = os.path.join(path, 'wav')
    if not os.path.isdir(wav_dir):
        logging.error('Path %s does not exist.', wav_dir)
    tg_dir = os.path.join(path, 'tg')
    if not os.path.isdir(tg_dir):
        logging.error('Path %s does not exist.', tg_dir)
    text_dir = os.path.join(path, 'text')
    if not os.path.isdir(text_dir):
        logging.error('Path %s does not exist.', text_dir)
    cache_dir = os.path.join(path, 'cache')
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    ppg_deps = DependenciesPPG()
    for wav_file in glob(os.path.join(wav_dir, '*.wav')):
        basename = os.path.basename(wav_file).split('.')[0]
        cache_file = os.path.join(cache_dir, basename + '.proto')
        if skip_exist and os.path.isfile(cache_file):
            logging.info('Skip existing cache.')
            continue
        utt_id = '%s_%s' % (speaker_id, basename)
        logging.info('Processing utterance %s', utt_id)
        wavio_obj = wavio.read(wav_file)
        fs = wavio_obj.rate
        wav = wavio_obj.data
        tg_file = os.path.join(tg_dir, basename + '.TextGrid')
        tg = TextGrid()
        tg.read(tg_file)
        text_file = os.path.join(text_dir, basename + '.lab')
        with open(text_file, 'r') as reader:
            text = reader.readline()
        start = time.time()
        utt = process_utt(wav, fs, text, tg, ppg_deps)
        end = time.time()
        logging.info('Took %1.2f second(s).', end - start)
        utt.speaker_id = speaker_id
        utt.utterance_id = utt_id
        utt.original_file = wav_file
        if len(dialect) > 0:
            utt.dialect = dialect
        if len(gender) > 0:
            utt.gender = gender
        utt.write(cache_file)


def main(path, skip_exist=True):
    """Process all speakers.

    Args:
        path: Root dir to all speaker data and the metadata file.
        skip_exist: [optional] If True then skip files that have already cached.
    """
    meta_data_file = os.path.join(path, 'metadata')
    with open(meta_data_file, 'r') as reader:
        for ii, line in enumerate(reader):
            if ii == 0:
                # Skip the header
                continue
            name, gender, dialect = line.split()
            curr_path = os.path.join(path, name)
            process_speaker(curr_path, gender, dialect, skip_exist)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    root_dir = '/data_repo/mpd'
    start = time.time()
    main(root_dir, True)
    end = time.time()
    logging.info('All the steps took %f seconds.', end - start)
