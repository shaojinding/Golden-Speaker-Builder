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

"""Pytorch dataset class for L2-ARCTIC MPD annotations.

This module reads pre-cached files and computes phoneme-level feature vectors.
Once initialized, you should not modify the dataset anymore. Rather, if you
do need to create a dataset from another set of files, create a new dataset
object. Modifying existing dataset object will lead to un-defined behaviors,
and the object does not have safeguards for that!
"""

import os
import logging
import numpy as np
import torch
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import default_collate
from mpd import UtteranceMPD, AnnotationErrorType


class L2ArcticMPDset(Dataset):
    def __init__(self, file_list: list, sym_table: dict, keep_phonemes='all',
                 keep_annotations='all', is_rm_sil=True):
        """Create an L2-ARCTIC MPD dataset object for pytorch.

        Args:
            file_list: A list of file paths; each path points to a DataUtterance
            protocol buffer binary file.
            sym_table: A phoneme symbol table represented in a dictionary.
            keep_phonemes: [optional] A set or string 'all'. The set will
            contain phoneme symbols, and only the instances of these symbols
            will be retained in the loaded dataset. If set to 'all', then the
            class will keep all the phoneme instances defined in the sym_table.
            keep_annotations: [optional] A set or string 'all'. The set will
            contain annotations tags, and only the instances of these tags will
            be retained in the loaded dataset. If set to 'all', then the class
            will keep all the annotations. The possible annotation tags are,
                - 's': substitution
                - 'a': addition/insertion
                - 'd': deletion/omission
                - 'c': correct
            No matter which set of symbols you choose, 'c' will be
            automatically added.
            is_rm_sil: [optional] If set to True then all instances of 'sil'
            will be removed, otherwise they will be retained. However I don't
            think you should keep the silence segments since predicting
            mispronunciation on a silent sounds does not make sense.

        Values initialized:
            file_list: A sorted list containing all the files that are used
            in creating this dataset since there might be invalid paths in the
            input list.
            feats: A T*D numpy array. Containing phoneme level MPD features.
            labels: A T*2 numpy array. Containing the MPD tag and canonical
            phoneme label for each corresponding feature vector. The error tags
            are binary, 0 for correct pronunciation and 1 for mispronunciation.
            The phoneme labels are numeric, defined by the sym_table.
        """
        file_list.sort()
        self.file_list = []
        self.feats = None
        self.labels = []

        # Figure out which phonemes should we keep.
        if keep_phonemes is 'all':
            keep_phonemes = set(sym_table.keys())
        # Change to all lower case
        keep_phonemes = set([val.lower() for val in keep_phonemes])

        # Flag that we should also remove all 'sil' segments if required.
        # Generally we should always set 'is_rm_sil' to True because it does not
        # make sense to predict mispronunciations on silence.
        if is_rm_sil:
            if 'sil' in keep_phonemes:
                keep_phonemes.remove('sil')

        # Figure out which annotations we should keep. Generally we should set
        # this to only 's' and 'c'. 'c' stands for correct.
        if keep_annotations is 'all':
            keep_annotations = {'s', 'a', 'd', 'c'}
        else:
            keep_annotations.add('c')

        for each_cache in file_list:
            if not os.path.isfile(each_cache):
                logging.warning('Cache file %s does not exist, skip.',
                                each_cache)
                continue
            self.file_list.append(each_cache)
            utt = UtteranceMPD()
            utt.read(each_cache)

            # Figure out which segments to keep
            num_phones = len(utt.phone)
            keep_idx = np.zeros(num_phones, dtype=bool)
            utt.set_error_tag()

            for ii, each_interval in enumerate(utt.phone.intervals):
                curr_phoneme = each_interval.mark

                # Figure out error type.
                curr_annotation = ''
                if utt.error_tag[ii] is AnnotationErrorType.correct:
                    curr_annotation = 'c'
                elif utt.error_tag[ii] is AnnotationErrorType.substitution:
                    curr_annotation = 's'
                elif utt.error_tag[ii] is AnnotationErrorType.addition:
                    curr_annotation = 'a'
                elif utt.error_tag[ii] is AnnotationErrorType.deletion:
                    curr_annotation = 'd'

                # Only keep the segment if it is a required phoneme and has the
                # required annotation tag.
                if (curr_phoneme in keep_phonemes) and (curr_annotation in
                                                        keep_annotations):
                    keep_idx[ii] = True
                    if curr_annotation is 'c':
                        # 0 for correct
                        self.labels.append([0, sym_table[curr_phoneme]])
                    else:
                        # 1 for error
                        self.labels.append([1, sym_table[curr_phoneme]])

            if keep_idx.any():
                # Get hu_feat.
                utt.set_hu_feat(sym_table)
                hu_feat = utt.hu_feat[keep_idx, :]
                if self.feats is not None:
                    self.feats = np.concatenate((self.feats, hu_feat), 0)
                else:
                    self.feats = np.copy(hu_feat)
            else:
                # No segment in this utterance matches the requirements.
                continue
        self.labels = np.array(self.labels)
        num_feat = self.feats.shape[0]
        num_lab = self.labels.shape[0]
        assert num_feat == num_lab, \
            'Label and feature length mismatch. %d vs %d.' % (num_feat, num_lab)
        assert self.labels.shape[1] == 2, 'The label should be 2-dim.'

    def __getitem__(self, item: int):
        """Get the i-th feature and label vectors.

        Args:
            item: Array index.

        Returns:
            data: A D-dim torch Tensor, shape is (D)
            label: A 2-dim torch Tensor, shape is (2)
        """
        if item >= self.__len__():
            raise IndexError('Index %d is out of range', item)
        data = torch.from_numpy(self.feats[item, :]).reshape(-1)
        label = torch.from_numpy(self.labels[item, :]).reshape(-1)
        return data, label

    def __len__(self):
        """Get the number of samples in the dataset.

        Returns:
            The total number of feature vectors in this dataset.
        """
        return self.labels.shape[0]


class L2ArcticMPDsetSeq(Dataset):
    def __init__(self, file_list: list, sym_table: dict, keep_phonemes='all',
                 keep_annotations='all', is_rm_sil=True):
        """Create an L2-ARCTIC MPD dataset object for pytorch.

        This class loads sequential features.

        Args:
            file_list: A list of file paths; each path points to a DataUtterance
            protocol buffer binary file.
            sym_table: A phoneme symbol table represented in a dictionary.
            keep_phonemes: [optional] A set or string 'all'. The set will
            contain phoneme symbols, and only the instances of these symbols
            will be retained in the loaded dataset. If set to 'all', then the
            class will keep all the phoneme instances defined in the sym_table.
            keep_annotations: [optional] A set or string 'all'. The set will
            contain annotations tags, and only the instances of these tags will
            be retained in the loaded dataset. If set to 'all', then the class
            will keep all the annotations. The possible annotation tags are,
                - 's': substitution
                - 'a': addition/insertion
                - 'd': deletion/omission
                - 'c': correct
            No matter which set of symbols you choose, 'c' will be
            automatically added.
            is_rm_sil: [optional] If set to True then all instances of 'sil'
            will be removed, otherwise they will be retained. However I don't
            think you should keep the silence segments since predicting
            mispronunciation on a silent sounds does not make sense.

        Values initialized:
            file_list: A sorted list containing all the files that are used
            in creating this dataset since there might be invalid paths in the
            input list.
            feats: A T-element list. Each element is an L(varied)*D numpy array
            containing phoneme level MPD sequential features.
            labels: A T*2 numpy array. Containing the MPD tag and canonical
            phoneme label for each corresponding feature vector. The error tags
            are binary, 0 for correct pronunciation and 1 for mispronunciation.
            The phoneme labels are numeric, defined by the sym_table.
            length: A list of integers each represents the length of the
            corresponding data sequence.
            feature_dim: A scalar, the number of feature dimensions.
        """
        file_list.sort()
        self.file_list = []
        self.feats = []
        self.labels = []
        self.length = []
        self.feature_dim = None

        # Figure out which phonemes should we keep.
        if keep_phonemes is 'all':
            keep_phonemes = set(sym_table.keys())
        # Change to all lower case
        keep_phonemes = set([val.lower() for val in keep_phonemes])

        # Flag that we should also remove all 'sil' segments if required.
        # Generally we should always set 'is_rm_sil' to True because it does not
        # make sense to predict mispronunciations on silence.
        if is_rm_sil:
            if 'sil' in keep_phonemes:
                keep_phonemes.remove('sil')

        # Figure out which annotations we should keep. Generally we should set
        # this to only 's' and 'c'. 'c' stands for correct.
        if keep_annotations is 'all':
            keep_annotations = {'s', 'a', 'd', 'c'}
        else:
            keep_annotations.add('c')

        for each_cache in file_list:
            if not os.path.isfile(each_cache):
                logging.warning('Cache file %s does not exist, skip.',
                                each_cache)
                continue
            self.file_list.append(each_cache)
            utt = UtteranceMPD()
            utt.read(each_cache)

            # Figure out which segments to keep
            keep_idx = []
            utt.set_error_tag()

            for ii, each_interval in enumerate(utt.phone.intervals):
                curr_phoneme = each_interval.mark

                # Figure out error type.
                curr_annotation = ''
                if utt.error_tag[ii] is AnnotationErrorType.correct:
                    curr_annotation = 'c'
                elif utt.error_tag[ii] is AnnotationErrorType.substitution:
                    curr_annotation = 's'
                elif utt.error_tag[ii] is AnnotationErrorType.addition:
                    curr_annotation = 'a'
                elif utt.error_tag[ii] is AnnotationErrorType.deletion:
                    curr_annotation = 'd'

                # Only keep the segment if it is a required phoneme and has the
                # required annotation tag.
                if (curr_phoneme in keep_phonemes) and (curr_annotation in
                                                        keep_annotations):
                    keep_idx.append(ii)
                    if curr_annotation is 'c':
                        # 0 for correct
                        self.labels.append([0, sym_table[curr_phoneme]])
                    else:
                        # 1 for error
                        self.labels.append([1, sym_table[curr_phoneme]])

            if keep_idx:
                # Get hu_feat.
                utt.set_hu_feat(sym_table, is_sequential=True)
                hu_feat = [utt.hu_feat[i] for i in keep_idx]
                self.length.extend([val.shape[0] for val in hu_feat])
                if self.feats:
                    self.feats.extend(hu_feat)
                else:
                    self.feats = hu_feat
                # Figure out the feature dimension
                if self.feature_dim is None:
                    for val in hu_feat:
                        if val.shape[0] > 1:
                            self.feature_dim = val.shape[1]
                            break
            else:
                # No segment in this utterance matches the requirements.
                continue
        self.labels = np.array(self.labels)
        num_feat = len(self.feats)
        num_lab = self.labels.shape[0]
        assert num_feat == num_lab, \
            'Label and feature length mismatch. %d vs %d.' % (num_feat, num_lab)
        assert self.labels.shape[1] == 2, 'The label should be 2-dim.'
        assert self.feature_dim is not None, 'Feature dimension error.'

    def __getitem__(self, item: int):
        """Get the i-th feature and label vectors.

        Args:
            item: Array index.

        Returns:
            data: A L*D torch Tensor, shape is (L, D)
            label: A 2-dim torch Tensor, shape is (1, 2)
            length: An int.
        """
        if item >= self.__len__():
            raise IndexError('Index %d is out of range', item)
        data = torch.from_numpy(self.feats[item]).reshape(-1, self.feature_dim)
        label = torch.from_numpy(self.labels[item, :]).reshape(1, -1)
        length = self.length[item]
        return data, label, length

    def __len__(self):
        """Get the number of samples in the dataset.

        Returns:
            The total number of feature vectors in this dataset.
        """
        return self.labels.shape[0]


def sequence_collate(batch):
    """Collate function to pad sequential.

    Args:
        batch: A list of tuples (data, label, length). Consider this is the
        return value of [val for val in dataset], where dataset is an instance
        of L2ArcticMPDsetSeq.

    Returns:
        seq_tensor: A (batch_size, num_frames, feature_dim) tensor.
        labels: A (batch_size, 1, 2) tensor.
        input_length: A list that has batch_size elements.
    """
    # If you iterate this list 'transposed', it has three elements, which are,
    # - tuple of data, each is an (L(varied), D) tensor
    # - tuple of label, each is a (2) tensor
    # - tuple of data length, each is an int
    transposed = [val for val in zip(*batch)]
    sort_idx = np.argsort(1/np.array(transposed[2]))  # Sort in descending order
    input_data = [transposed[0][i] for i in sort_idx]
    input_label = [transposed[1][i] for i in sort_idx]
    input_length = [int(transposed[2][i]) for i in sort_idx]

    batch_size = len(batch)
    max_length = max(input_length)
    feature_dim = None
    for val in input_data:
        if val.shape[0] > 1:
            feature_dim = val.shape[1]
            break
    assert feature_dim is not None, 'Feature dimension error.'

    # Create padded batch
    # Dump padding everywhere, and place seqs on the left.
    seq_tensor = torch.zeros(batch_size, max_length, feature_dim)
    for idx, seqlen in enumerate(input_length):
        seq_tensor[idx, 0:seqlen, :] = input_data[idx]

    # Labels can be dealt using the default manner.
    labels = default_collate(input_label)

    return seq_tensor, labels, input_length
