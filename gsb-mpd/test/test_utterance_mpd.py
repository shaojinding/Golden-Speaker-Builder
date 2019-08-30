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

import unittest
import numpy as np
from common import utterance
from mpd import UtteranceMPD, AnnotationErrorType,\
    diagnosis_phoneme_recognition, get_mpd_model_v0, L2ArcticFCnetJoint,\
    get_mpd_model_v1, get_mpd_model_v2, get_mpd_model_v3, L2ArcticRNNv0
import wavio
from textgrid import TextGrid
from ppg import DependenciesPPG, compute_monophone_ppg
from common.feat import read_wav_kaldi_internal
from torch import tensor


class TestUtteranceMPD(unittest.TestCase):
    def setUp(self):
        wavio_obj = wavio.read('data/air.wav')
        fs = wavio_obj.rate
        wav = wavio_obj.data
        text = 'air'
        tg = TextGrid()
        tg.read('data/air.TextGrid')
        self.utt = UtteranceMPD(wav, fs, text)
        self.utt.kaldi_shift = 5.0
        self.utt.align = tg
        ppg_fixtures = DependenciesPPG()
        wd = read_wav_kaldi_internal(self.utt.wav, self.utt.fs)
        self.utt.monophone_ppg = compute_monophone_ppg(
            wd, ppg_fixtures.nnet, ppg_fixtures.lda,
            ppg_fixtures.monophone_trans, self.utt.kaldi_shift)
        phone_tier = utterance.time_to_frame_interval_tier(
            tg.getFirst('phones'), self.utt.kaldi_shift)
        phone_tier = utterance.normalize_tier_mark(phone_tier)
        self.utt.phone = phone_tier
        self.sym_table = utterance.read_sym_table('data/phoneme_table')

    def tearDown(self):
        pass

    def test_set_hu_feat(self):
        self.utt.set_hu_feat(self.sym_table, is_sequential=False)

        # Make sure we get a T*D matrix
        self.assertEqual(self.utt.hu_feat.shape,
                         (len(self.utt.phone.intervals),
                          self.utt.monophone_ppg.shape[1] * 2))

        # Make sure the values are reasonable - there is no "nan"
        self.assertFalse(np.isnan(self.utt.hu_feat).any())

    def test_set_hu_feat_sequential(self):
        self.utt.set_hu_feat(self.sym_table, is_sequential=True)

        # Make sure we get a T-ele list.
        self.assertEqual(len(self.utt.hu_feat), len(self.utt.phone.intervals))

        # Make sure the values are reasonable - there is no "nan"
        for each_seq in self.utt.hu_feat:
            self.assertFalse(np.isnan(each_seq).any())

    def test_set_error_tag(self):
        self.utt.set_error_tag()
        # Look at data/air.TextGrid
        correct_answer = [AnnotationErrorType.deletion,
                          AnnotationErrorType.substitution,
                          AnnotationErrorType.addition,
                          AnnotationErrorType.correct]
        self.assertEqual(correct_answer, self.utt.error_tag)

    def test_diagnosis_phoneme_recognition_ndarray(self):
        scores = np.array([1.0, 2.0, 3.0, 4.0])
        index = 3
        best = diagnosis_phoneme_recognition(scores, index)
        self.assertEqual(best, 2)

    def test_diagnosis_phoneme_recognition_tensor(self):
        scores = tensor([1, 2, 3, 4])
        index = 3
        best = diagnosis_phoneme_recognition(scores, index)
        self.assertEqual(best, 2)

    def test_get_mpd_model_v0_no_cache(self):
        mdls = get_mpd_model_v0(False)
        self.assertEqual(len(mdls), 39)
        self.assertTrue(all([isinstance(val, str) for val in mdls.values()]))

    def test_get_mpd_model_v0_cache(self):
        mdls = get_mpd_model_v0(True)
        self.assertEqual(len(mdls), 39)
        self.assertTrue(all([
            isinstance(val, L2ArcticFCnetJoint) for val in mdls.values()]))

    def test_get_mpd_model_v1(self):
        model = get_mpd_model_v1('data/model/fc_joint/mdl.ckpt')
        self.assertTrue(isinstance(model, L2ArcticFCnetJoint))

    def test_get_mpd_model_v2(self):
        mdls = get_mpd_model_v2('data/model/rnn_separate')
        self.assertTrue(all([
            isinstance(val, L2ArcticRNNv0) for val in mdls.values()]))

    def test_get_mpd_model_v3(self):
        model = get_mpd_model_v3('data/model/rnn_joint/mdl.ckpt')
        self.assertTrue(isinstance(model, L2ArcticRNNv0))

    def test_prepare_for_mpd_valid(self):
        self.utt.prepare_for_mpd()

    def test_prepare_for_mpd_invalid(self):
        try:
            self.utt.prepare_for_mpd(0.5)
        except ValueError:
            pass

    def test_run_prediction_v0_model_path(self):
        models = get_mpd_model_v0(False)
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v0(models, 0.3)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v0_model_cache(self):
        models = get_mpd_model_v0(True)
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v0(models, 0.3)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v0_separated_thresholds(self):
        models = get_mpd_model_v0(False)
        thresholds = dict((k, 0.3) for k in models.keys())
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v0(models, thresholds)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v1_model(self):
        models = get_mpd_model_v1('data/model/fc_joint/mdl.ckpt')
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v1(models, 0.3)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v1_separated_thresholds(self):
        models = get_mpd_model_v1('data/model/fc_joint/mdl.ckpt')
        thresholds = dict((k, 0.3) for k in self.sym_table.keys())
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v1(models, thresholds)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v2_model(self):
        models = get_mpd_model_v2('data/model/rnn_separate')
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v2(models, 0.3)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v2_separated_thresholds(self):
        models = get_mpd_model_v2('data/model/rnn_separate')
        thresholds = dict((k, 0.3) for k in models.keys())
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v2(models, thresholds)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v3_model(self):
        models = get_mpd_model_v3('data/model/rnn_joint/mdl.ckpt')
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v3(models, 0.3)
        self.assertEqual(len(tg), 5)

    def test_run_prediction_v3_separated_thresholds(self):
        models = get_mpd_model_v3('data/model/rnn_joint/mdl.ckpt')
        thresholds = dict((k, 0.3) for k in self.sym_table.keys())
        self.utt.prepare_for_mpd()
        tg = self.utt.run_prediction_v3(models, thresholds)
        self.assertEqual(len(tg), 5)
