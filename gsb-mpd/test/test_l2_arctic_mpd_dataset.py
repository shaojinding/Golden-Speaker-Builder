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
from mpd import L2ArcticMPDset, L2ArcticMPDsetSeq, sequence_collate
from glob import glob
from common.utterance import read_sym_table


class TestL2ArcticMpdDataset(unittest.TestCase):
    def setUp(self):
        self.test_files = glob('data/l2_arctic_cache/*.proto')
        self.sym_table = read_sym_table('data/phoneme_table')
        self.dataset = L2ArcticMPDset(self.test_files, self.sym_table)

    def tearDown(self):
        pass

    def test_load_dataset_full(self):
        dataset = L2ArcticMPDset(self.test_files, self.sym_table)
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_phoneme(self):
        dataset = L2ArcticMPDset(self.test_files, self.sym_table, {'Z'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_error_type(self):
        dataset = L2ArcticMPDset(self.test_files, self.sym_table,
                                 keep_annotations={'s', 'd'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_combined(self):
        dataset = L2ArcticMPDset(self.test_files, self.sym_table, {'Z'},
                                 keep_annotations={'s'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_iterate_dataset_valid(self):
        data, label = self.dataset[0]

    def test_iterate_dataset_invalid(self):
        count = len(self.dataset)
        try:
            data, label = self.dataset[count]
        except IndexError:
            pass

    def test_count_dataset(self):
        count = len(self.dataset)
        self.assertEqual(count, self.dataset.feats.shape[0])


class TestL2ArcticMpdDatasetSeq(unittest.TestCase):
    def setUp(self):
        self.test_files = glob('data/l2_arctic_cache/*.proto')
        self.sym_table = read_sym_table('data/phoneme_table')
        self.dataset = L2ArcticMPDsetSeq(self.test_files, self.sym_table)

    def tearDown(self):
        pass

    def test_load_dataset_full(self):
        dataset = L2ArcticMPDsetSeq(self.test_files, self.sym_table)
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_phoneme(self):
        dataset = L2ArcticMPDsetSeq(self.test_files, self.sym_table, {'Z'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_error_type(self):
        dataset = L2ArcticMPDsetSeq(self.test_files, self.sym_table,
                                    keep_annotations={'s', 'd'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_load_dataset_subset_combined(self):
        dataset = L2ArcticMPDsetSeq(self.test_files, self.sym_table, {'Z'},
                                    keep_annotations={'s'})
        self.assertTrue(dataset.labels[:, 0].sum() > 0)

    def test_iterate_dataset_valid(self):
        for data, label, length in self.dataset:
            self.assertEqual(data.shape[0], length)
            self.assertEqual(label.shape[0], 1)
            self.assertEqual(label.shape[1], 2)

    def test_iterate_dataset_invalid(self):
        count = len(self.dataset)
        try:
            data, label, length = self.dataset[count]
        except IndexError:
            pass

    def test_count_dataset(self):
        count = len(self.dataset)
        self.assertEqual(count, len(self.dataset.feats))

    def test_seq_collate(self):
        indices = [0, 1, 2, 3]
        batch_size = len(indices)
        batch = [self.dataset[i] for i in indices]
        seq_tensor, labels, lengths = sequence_collate(batch)
        max_length = max(lengths)

        self.assertEqual(seq_tensor.shape[0], batch_size)
        self.assertEqual(seq_tensor.shape[1], max_length)
        self.assertEqual(labels.shape[0], batch_size)
        self.assertEqual(labels.shape[1], 1)
        self.assertEqual(labels.shape[2], 2)
        self.assertTrue(sorted(lengths, reverse=True) == lengths)
