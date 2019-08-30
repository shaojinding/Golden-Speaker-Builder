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

"""This module provides a data utterance class for the MPD task."""

import os
import numpy as np
import logging
import torch
from enum import Enum
from common import utterance
from mpd import L2ArcticFCnetJoint, L2ArcticRNNv0
from textgrid import IntervalTier

# Static resources.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                        'data')
# Path to the dir that stores all phoneme-dependent MPD models.
MPD_SEPARATED_MDLS_PATH = os.path.join(DATA_DIR, 'mpd_mdls_separated')


def diagnosis_phoneme_recognition(score, index):
    """Perform a diagnosis by doing a phoneme recognition.

    Recognize the most likely phoneme besides the canonical pronunciation.

    Args:
        score: An array-like object with the argmax method. E.g. ndarray, tensor
        index: The index of the canonical pronunciation.

    Returns:
        The index of the most likely phoneme aside from the canonical one.
    """
    min_score = score.min()
    score[index] = min_score - 1
    return int(score.argmax())


def get_mpd_model_v0(is_pre_cache=False, model_root=None):
    """Get the model path/object dictionary for fully-connected MPD models.

    Args:
        is_pre_cache: [optional] If set to True then will load all models,
        otherwise will only save the model paths.
        model_root: [optional] If set will look for models in this dir.

    Returns:
        models: A dict whose keys are phonemes and values are the path to the
        corresponding MPD PyTorch models (is_pre_cache=False) or the pre-loaded
        PyTorch models (is_pre_cache=True).
    """
    if not model_root:
        model_root = MPD_SEPARATED_MDLS_PATH

    phonemes = utterance.get_hardcoded_sym_table().keys()
    models = {}
    for each_phoneme in phonemes:
        if each_phoneme == 'sil':
            continue
        mdl_path = os.path.join(model_root,
                                'mdl_%s.ckpt' % each_phoneme)
        if is_pre_cache:
            curr_mdl = L2ArcticFCnetJoint(80, 40, 1)
            curr_mdl.load_state_dict(torch.load(mdl_path, map_location='cpu'))
            models[each_phoneme] = curr_mdl
        else:
            models[each_phoneme] = mdl_path
    return models


def get_mpd_model_v1(model_path):
    """Load the joint fully-connected MPD model.

    Args:
        model_path: Path to a joint fully-connected model.

    Returns:
        model: A pre-loaded PyTorch model.
    """
    model = L2ArcticFCnetJoint(80, 40, 39)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    return model


def get_mpd_model_v2(model_root):
    """Get the model object dictionary for RNN MPD models.

    Args:
        model_root: Will look for models in this dir.

    Returns:
        models: A dict whose keys are phonemes and values are the pre-loaded
        PyTorch models.
    """
    phonemes = utterance.get_hardcoded_sym_table().keys()
    models = {}
    for each_phoneme in phonemes:
        if each_phoneme == 'sil':
            continue
        mdl_path = os.path.join(model_root,
                                'mdl_%s.ckpt' % each_phoneme)
        curr_mdl = L2ArcticRNNv0(80, 40, 2, 1, 'LSTM', 0.5, True, False)
        curr_mdl.load_state_dict(torch.load(mdl_path, map_location='cpu'))
        models[each_phoneme] = curr_mdl
    return models


def get_mpd_model_v3(model_path):
    """Load the joint RNN MPD model.

    Args:
        model_path: Path to a joint fully-connected model.

    Returns:
        model: A pre-loaded PyTorch model.
    """
    model = L2ArcticRNNv0(80, 40, 2, 39, 'LSTM', 0.5, True, False)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    return model


class UtteranceMPD(utterance.Utterance):
    def __init__(self, wav=None, fs=-1, text=''):
        """Inputs are the same as the base class."""
        super(UtteranceMPD, self).__init__(wav, fs, text)
        # A T*D feature matrix, T is the number of phones.
        self.hu_feat = None
        # A list of AnnotationErrorType object, each corresponding to one phone.
        self.error_tag = None
        # Pronunciation score assigned by a classifier.
        self.score = None
        # The error predictions.
        self.prediction = None
        # The extra pronunciation diagnostic information.
        self.diagnosis = None

    def set_hu_feat(self, sym_table: dict, is_sequential=False):
        """Compute equation (15) in the following paper,

        @article{hu2015improved,
          title = "Improved mispronunciation detection with deep neural network
          trained acoustic models and transfer learning based logistic
          regression classifiers",
          journal = "Speech Communication",
          volume = "67",
          pages = "154 - 166",
          year = "2015",
          issn = "0167-6393",
          doi = "https://doi.org/10.1016/j.specom.2014.12.008",
          url = "http://www.sciencedirect.com/science/article/pii/S0167639314001010",
          author = "Wenping Hu and Yao Qian and Frank K. Soong and Yong Wang",
          keywords = "Computer-aided language learning, Mispronunciation
          detection, Deep neural network, Logistic regression, Transfer
          learning"
        }

        Args:
            sym_table: Phoneme symbol table to translate the phoneme labels
            into PPG dimensions.
            is_sequential: If set to true, then for each phoneme it will return
            the whole sequence of feature vectors instead of their average.

        Returns:
            is_sequential==False (default): Set hu_feat to T*D matrix, one
            feature vector per phone segment.
            is_sequential==True: Set hu_feat to a T-element list. Each element
            is an L(varied)*D numpy array containing sequential MPD feature
            vectors for each phone segment.
        """
        ppgs = self.monophone_ppg
        assert ppgs.size > 0, "Please extract monophone PPGs first."
        num_ppg_frame, num_ppg_dim = ppgs.shape
        phones = self.phone
        num_phones = len(phones.intervals)
        assert num_phones > 0, "Please set phone intervals first."
        if not is_sequential:
            # T*D feature matrix, the feature is the concatenation of LPPs and
            # LPRs
            self.hu_feat = np.zeros((num_phones, num_ppg_dim * 2))
        else:
            self.hu_feat = []

        if num_ppg_frame < phones.maxTime:
            logging.warning("PPG frame number %d is less then the max time %d",
                            num_ppg_frame, phones.maxTime)

        max_frame_idx = num_ppg_frame - 1
        for ii, each_phone in enumerate(phones.intervals):
            start_idx = each_phone.minTime
            # Deal with potential mismatch between PPG frames and alignment
            end_idx = min([each_phone.maxTime, max_frame_idx])
            # Deal with the case that the segment is too short
            if start_idx == end_idx:
                end_idx += 1
            if end_idx > max_frame_idx:
                raise ValueError("Some segments are too short!")

            # The phone segment is bounded by [start_idx, end_idx), i.e., not
            # including the ending frame.
            curr_ppgs = ppgs[int(start_idx):int(end_idx), :]

            # Equations (7) and (8)
            # LPP stands for Log Phone Posterior
            # For a phone segment with label "q", the LPP score is,
            # LPP(q) = log p(q|o;t_s,t_e) ~ 1/(t_e-t_s+1)sum(log(p(q|o_t))
            lpps = np.log(curr_ppgs + np.finfo(curr_ppgs.dtype).eps)  # Avoid 0
            if not is_sequential:
                lpps = lpps.mean(0)  # Average over time axis

            curr_phone = each_phone.mark
            if curr_phone in sym_table:
                curr_phone_idx = sym_table[curr_phone]
            else:
                logging.warning("Phoneme %s is not in the symbol table, "
                                "treating it as ""sil""", curr_phone)
                curr_phone_idx = sym_table["sil"]

            # Equation (14)
            # LPR stands for Log Posterior Ratio
            # For a phoneme pair "q" and "v", the LPR score is,
            # LPR(q|v) = log p(q|o;t_s,t_e)-log p(v|o;t_s,t_e) = LPP(q)-LPP(v)
            # One of LPR(q|v)'s is in fact the GOP score
            # Here lpps is the LPP scores for a phone segment ('q'), and idx
            # means that lpps(idx) = LPP(q)
            # This step keeps the LPR(q|q) score, which is zero, to make the
            # feature dimensions consistent across different phonemes; this does
            # not affect the nnet classifiers
            if not is_sequential:
                lprs = lpps - lpps[curr_phone_idx]
            else:
                lprs = (lpps.transpose() - lpps[:, curr_phone_idx]).transpose()

            # Save the current feature(s)
            if not is_sequential:
                self.hu_feat[ii, :] = np.concatenate((lpps, lprs), 0)
            else:
                self.hu_feat.append(np.concatenate((lpps, lprs), 1))

    def set_error_tag(self):
        """Obtain the error tags from the annotations.

        Annotations are saved in the align field.
        """
        assert len(self.align.tiers) > 0, "Please get annotations first."
        annotation_tier = self.align.getFirst("phones")
        annotation_tier = utterance.normalize_tier_mark(
            annotation_tier, "NormalizePhoneAnnotation")
        self.error_tag = []
        for each_interval in annotation_tier.intervals:
            parse_tag = each_interval.mark.split(",")
            if len(parse_tag) == 1:
                self.error_tag.append(AnnotationErrorType.correct)
            elif len(parse_tag) == 3:
                if parse_tag[2] is "s":
                    self.error_tag.append(AnnotationErrorType.substitution)
                elif parse_tag[2] is "d":
                    self.error_tag.append(AnnotationErrorType.deletion)
                elif parse_tag[2] is "a":
                    self.error_tag.append(AnnotationErrorType.addition)
                else:
                    raise ValueError("Error type %s is not valid.",
                                     parse_tag[2])
            else:
                raise ValueError("Annotation %s is not valid.",
                                 each_interval.mark)

    def assemble_mpd_results(self):
        """Append MPD results to align.

        Returns:
            tg: TextGrid with MPD result tiers.
        """
        if self.prediction is None or self.score is None or self.diagnosis is\
                None:
            logging.error('Please run MPD first.')

        tg = self.align
        # Clean previous results, if any.
        remove_tier_idx = []
        for i, name in enumerate(tg.getNames()):
            if name in {'predictions', 'scores', 'diagnoses'}:
                # To make sure that removing the previous item does not affect
                # removing the next one.
                remove_tier_idx.insert(0, i)
        for idx in remove_tier_idx:
            tg.pop(idx)

        phone_tier = tg.getFirst('phones')
        prediction_tier = IntervalTier('predictions', phone_tier.minTime,
                                       phone_tier.maxTime)
        score_tier = IntervalTier('scores', phone_tier.minTime,
                                  phone_tier.maxTime)
        diagnosis_tier = IntervalTier('diagnoses', phone_tier.minTime,
                                      phone_tier.maxTime)

        for ii, each_predict in enumerate(self.prediction):
            predict_mark = '' if each_predict == 0 else 'sub_error'
            min_time = phone_tier[ii].minTime
            max_time = phone_tier[ii].maxTime
            prediction_tier.add(min_time, max_time, predict_mark)
            score_mark = '%1.2f' % self.score[ii]
            score_tier.add(min_time, max_time, score_mark)
            diagnosis_tier.add(min_time, max_time, self.diagnosis[ii])
        tg.append(prediction_tier)
        tg.append(diagnosis_tier)
        tg.append(score_tier)
        self.align = tg
        return tg

    def run_prediction_v0(self, models: dict, threshold=0.5):
        """Run MPD using a group of phoneme-dependent binary classifiers.

        This method will set score, prediction, and diagnosis.

        Args:
            models: A dict whose keys are phonemes and values are the path to
            the corresponding MPD PyTorch models/pre-loaded PyTorch models.
            threshold: A number in [0, 1] or a dict. When the threshold is a
            number, it is the global threshold for all classifiers, any
            classifier output greater than the threshold will be marked as an
            error. When the threshold is a dict, its keys are the phonemes and
            values are the phoneme-dependent thresholds. The keys must be the
            same as the ones in 'models'

        Returns:
            tg: TextGrid object with predictions, scores, and diagnosis.
        """
        # Check the models and threshold have the same set of keys,
        # if threshold is dict
        if isinstance(threshold, dict):
            if not set(models.keys()) == set(threshold.keys()):
                logging.error('threshold is not compatible with models.')
        else:
            # Convert singleton threshold to dict as well
            temp_threshold = {}
            for key in models:
                temp_threshold[key] = threshold
            threshold = temp_threshold

        # Figure out the value type of 'models'
        is_all_models_are_path = all([isinstance(val, str)
                                      for val in models.values()])
        is_all_models_are_cached = all([isinstance(val, L2ArcticFCnetJoint)
                                        for val in models.values()])
        if not (is_all_models_are_cached or is_all_models_are_path):
            logging.error('The input models can either contain all paths or '
                          'cached PyTorch models, please do not use mixed '
                          'dict values.')

        # Get classification features if not set
        sym_table = utterance.get_hardcoded_sym_table()
        reverse_sym_table = dict((v, k) for k, v in sym_table.items())
        if self.hu_feat is None:
            logging.info('Getting Hu''s features on the fly.')
            self.set_hu_feat(sym_table)

        # Convert feature to torch format
        feats = torch.from_numpy(self.hu_feat).type(torch.FloatTensor)

        # Perform classification
        if is_all_models_are_path:
            mpd_mdls = {}
        elif is_all_models_are_cached:
            mpd_mdls = models
        else:
            logging.error('Unknown error. Might have something to do with '
                          'these two flags. Good luck :)')
        self.score = []
        self.prediction = []
        self.diagnosis = []
        with torch.no_grad():
            for ii, each_phone in enumerate(self.phone.intervals):
                curr_phoneme = utterance.normalize_phone(each_phone.mark)
                if curr_phoneme == 'ax':
                    # These two phonemes are very similar so I just merged them.
                    logging.warning('Using the AH model for AX.')
                    curr_phoneme = 'ah'
                if utterance.is_sil(curr_phoneme):
                    # If is silence then skip it, assign it as correct.
                    logging.info('Skipping silence.')
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                curr_feat = feats[ii, :].view(-1, 1).transpose(0, 1)
                if curr_phoneme in mpd_mdls:
                    mdl = mpd_mdls[curr_phoneme]
                else:
                    if curr_phoneme in models and is_all_models_are_path:
                        mdl = L2ArcticFCnetJoint(curr_feat.shape[1], 40, 1)
                        mdl.load_state_dict(torch.load(models[curr_phoneme],
                                                       map_location='cpu'))
                    else:
                        mdl = None
                    mpd_mdls[curr_phoneme] = mdl
                if mdl is None:
                    # If there is no model for this phoneme then skip it, assign
                    # it as correct.
                    logging.warning('No model for the current phoneme %s, '
                                    'skipping and assume it is correct.',
                                    curr_phoneme)
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                else:
                    mdl.eval()

                curr_score = mdl(curr_feat)[0].numpy()
                self.score.append(curr_score)
                curr_predict = 0 if curr_score < threshold[curr_phoneme] else 1
                self.prediction.append(curr_predict)
                curr_phoneme_idx = sym_table[curr_phoneme]
                if curr_predict == 1:
                    # You may notice that I skipped the 40th dim, that is on
                    # purpose, because that one is silence
                    phoneme_rec = reverse_sym_table[
                        diagnosis_phoneme_recognition(
                            curr_feat[0, 0:39].reshape(-1), curr_phoneme_idx)]
                    self.diagnosis.append(phoneme_rec)
                else:
                    self.diagnosis.append('')

        return self.assemble_mpd_results()

    def run_prediction_v1(self, model, threshold=0.5):
        """Run MPD using a joint fully connected model.

        This method will set score, prediction, and diagnosis.

        Args:
            model: A PyTorch MPD model.
            threshold: A number in [0, 1] or a dict. When the threshold is a
            number, it is the global threshold for all classifiers, any
            classifier output greater than the threshold will be marked as an
            error. When the threshold is a dict, its keys are the phonemes and
            values are the phoneme-dependent thresholds. The keys must be the
            same as the ones in utterance.get_hardcoded_sym_table()

        Returns:
            tg: TextGrid object with predictions, scores, and diagnosis.
        """
        sym_table = utterance.get_hardcoded_sym_table()
        reverse_sym_table = dict((v, k) for k, v in sym_table.items())

        # Check the sym_table, model, and threshold are compatible.
        if isinstance(threshold, dict):
            if not set(sym_table.keys()) == set(threshold.keys()):
                logging.error('threshold is not compatible with sym_table.')
            if not model.fc2.out_features == len(threshold.keys()):
                logging.error('threshold is not compatible with the model.')
        else:
            # Convert singleton threshold to dict as well.
            temp_threshold = {}
            for key in sym_table:
                temp_threshold[key] = threshold
            threshold = temp_threshold

        # Get classification features if not set.
        if self.hu_feat is None:
            logging.info('Getting Hu''s features on the fly.')
            self.set_hu_feat(sym_table)

        # Convert feature to torch format
        feats = torch.from_numpy(self.hu_feat).type(torch.FloatTensor)

        self.score = []
        self.prediction = []
        self.diagnosis = []
        with torch.no_grad():
            for ii, each_phone in enumerate(self.phone.intervals):
                curr_phoneme = utterance.normalize_phone(each_phone.mark)
                curr_phoneme_idx = sym_table[curr_phoneme]
                if curr_phoneme == 'ax':
                    # These two phonemes are very similar so I just merged them.
                    logging.warning('Using the AH model for AX.')
                    curr_phoneme = 'ah'
                if utterance.is_sil(curr_phoneme):
                    # If is silence then skip it, assign it as correct.
                    logging.info('Skipping silence.')
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                if curr_phoneme_idx > (model.fc2.out_features - 1):
                    logging.error('We do not have a model for phoneme %s.',
                                  curr_phoneme)

                curr_feat = feats[ii, :].view(1, -1)
                curr_score = model(curr_feat)[0, curr_phoneme_idx].numpy()
                self.score.append(curr_score)
                curr_predict = 0 if curr_score < threshold[curr_phoneme] else 1
                self.prediction.append(curr_predict)

                if curr_predict == 1:
                    # You may notice that I skipped the 40th dim, that is on
                    # purpose, because that one is silence
                    phoneme_rec = reverse_sym_table[
                        diagnosis_phoneme_recognition(
                            curr_feat[0, 0:39].reshape(-1), curr_phoneme_idx)]
                    self.diagnosis.append(phoneme_rec)
                else:
                    self.diagnosis.append('')

        return self.assemble_mpd_results()

    def run_prediction_v2(self, models: dict, threshold=0.5):
        """Run MPD using a group of phoneme-dependent RNN binary classifiers.

        This method will set score, prediction, and diagnosis.

        Args:
            models: A dict whose keys are phonemes and values are pre-loaded
            PyTorch models.
            threshold: A number in [0, 1] or a dict. When the threshold is a
            number, it is the global threshold for all classifiers, any
            classifier output greater than the threshold will be marked as an
            error. When the threshold is a dict, its keys are the phonemes and
            values are the phoneme-dependent thresholds. The keys must be the
            same as the ones in 'models'

        Returns:
            tg: TextGrid object with predictions, scores, and diagnosis.
        """
        # Check the models and threshold have the same set of keys,
        # if threshold is dict
        if isinstance(threshold, dict):
            if not set(models.keys()) == set(threshold.keys()):
                logging.error('threshold is not compatible with models.')
        else:
            # Convert singleton threshold to dict as well
            temp_threshold = {}
            for key in models:
                temp_threshold[key] = threshold
            threshold = temp_threshold

        # Get classification features.
        sym_table = utterance.get_hardcoded_sym_table()
        reverse_sym_table = dict((v, k) for k, v in sym_table.items())
        logging.info('Getting Hu''s features on the fly.')
        self.set_hu_feat(sym_table, is_sequential=True)

        # Perform classification
        mpd_mdls = models
        self.score = []
        self.prediction = []
        self.diagnosis = []
        with torch.no_grad():
            for ii, each_phone in enumerate(self.phone.intervals):
                curr_phoneme = utterance.normalize_phone(each_phone.mark)
                if curr_phoneme == 'ax':
                    # These two phonemes are very similar so I just merged them.
                    logging.warning('Using the AH model for AX.')
                    curr_phoneme = 'ah'
                if utterance.is_sil(curr_phoneme):
                    # If is silence then skip it, assign it as correct.
                    logging.info('Skipping silence.')
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                if curr_phoneme in mpd_mdls:
                    mdl = mpd_mdls[curr_phoneme]
                else:
                    mdl = None
                if mdl is None:
                    # If there is no model for this phoneme then skip it, assign
                    # it as correct.
                    logging.warning('No model for the current phoneme %s, '
                                    'skipping and assume it is correct.',
                                    curr_phoneme)
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                else:
                    mdl.eval()

                curr_feat = torch.from_numpy(self.hu_feat[ii]).type(
                    torch.FloatTensor).view(1, -1, 80)
                hidden = mdl.init_hidden(1)
                seqlen = curr_feat.shape[1]
                curr_score = mdl(curr_feat,
                                 torch.LongTensor([seqlen]), hidden)[0].numpy()
                self.score.append(curr_score)
                curr_predict = 0 if curr_score < threshold[curr_phoneme] else 1
                self.prediction.append(curr_predict)
                curr_phoneme_idx = sym_table[curr_phoneme]
                if curr_predict == 1:
                    # You may notice that I skipped the 40th dim, that is on
                    # purpose, because that one is silence
                    phoneme_rec = reverse_sym_table[
                        diagnosis_phoneme_recognition(
                            curr_feat[0, :, 0:39].exp().mean(0).reshape(-1),
                            curr_phoneme_idx)]
                    self.diagnosis.append(phoneme_rec)
                else:
                    self.diagnosis.append('')

        return self.assemble_mpd_results()

    def run_prediction_v3(self, model, threshold=0.5):
        """Run MPD using a joint RNN model.

        This method will set score, prediction, and diagnosis.

        Args:
            model: A PyTorch MPD model.
            threshold: A number in [0, 1] or a dict. When the threshold is a
            number, it is the global threshold for all classifiers, any
            classifier output greater than the threshold will be marked as an
            error. When the threshold is a dict, its keys are the phonemes and
            values are the phoneme-dependent thresholds. The keys must be the
            same as the ones in utterance.get_hardcoded_sym_table()

        Returns:
            tg: TextGrid object with predictions, scores, and diagnosis.
        """
        sym_table = utterance.get_hardcoded_sym_table()
        reverse_sym_table = dict((v, k) for k, v in sym_table.items())

        # Check the sym_table, model, and threshold are compatible.
        if isinstance(threshold, dict):
            if not set(sym_table.keys()) == set(threshold.keys()):
                logging.error('threshold is not compatible with sym_table.')
            if not model.num_output == len(threshold.keys()):
                logging.error('threshold is not compatible with the model.')
        else:
            # Convert singleton threshold to dict as well.
            temp_threshold = {}
            for key in sym_table:
                temp_threshold[key] = threshold
            threshold = temp_threshold

        # Get classification features if not set.
        logging.info('Getting Hu''s features on the fly.')
        self.set_hu_feat(sym_table, is_sequential=True)

        # Run classification.
        self.score = []
        self.prediction = []
        self.diagnosis = []
        with torch.no_grad():
            for ii, each_phone in enumerate(self.phone.intervals):
                curr_phoneme = utterance.normalize_phone(each_phone.mark)
                curr_phoneme_idx = sym_table[curr_phoneme]
                if curr_phoneme == 'ax':
                    # These two phonemes are very similar so I just merged them.
                    logging.warning('Using the AH model for AX.')
                    curr_phoneme = 'ah'
                if utterance.is_sil(curr_phoneme):
                    # If is silence then skip it, assign it as correct.
                    logging.info('Skipping silence.')
                    self.prediction.append(0)
                    self.score.append(1)
                    self.diagnosis.append('')
                    continue
                if curr_phoneme_idx > (model.num_output - 1):
                    logging.error('We do not have a model for phoneme %s.',
                                  curr_phoneme)

                curr_feat = torch.from_numpy(self.hu_feat[ii]).type(
                    torch.FloatTensor).view(1, -1, 80)
                hidden = model.init_hidden(1)
                seqlen = curr_feat.shape[1]
                curr_score = model(curr_feat,
                                   torch.LongTensor([seqlen]),
                                   hidden)[0, curr_phoneme_idx].numpy()
                self.score.append(curr_score)
                curr_predict = 0 if curr_score < threshold[curr_phoneme] else 1
                self.prediction.append(curr_predict)

                if curr_predict == 1:
                    # You may notice that I skipped the 40th dim, that is on
                    # purpose, because that one is silence
                    phoneme_rec = reverse_sym_table[
                        diagnosis_phoneme_recognition(
                            curr_feat[0, :, 0:39].exp().mean(0).reshape(-1),
                            curr_phoneme_idx)]
                    self.diagnosis.append(phoneme_rec)
                else:
                    self.diagnosis.append('')

        return self.assemble_mpd_results()

    def prepare_for_mpd(self, shift=5):
        """Prepare necessary data for runtime MPD.

        Get the alignment, phone tier, monophone ppgs, and Hu's features.

        Args:
            shift: [optional] Frame shift (in ms) for Kaldi analysis.
        """
        self.kaldi_shift = shift
        self.get_alignment()
        self.get_phone_tier()
        self.get_monophone_ppg()
        self.set_hu_feat(utterance.get_hardcoded_sym_table())


class AnnotationErrorType(Enum):
    correct = 0
    substitution = 1
    deletion = 2
    addition = 3
