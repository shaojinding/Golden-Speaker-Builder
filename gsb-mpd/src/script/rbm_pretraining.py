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

"""This module performs RBM pre-training on the MPD data."""

import os
import torch
import datetime
import pickle
import time
from common import RBM
from common import utterance
from mpd import L2ArcticMPDset


if __name__ == '__main__':
    # Configuration
    BATCH_SIZE = 128
    VISIBLE_UNITS = 80  # 80-dim LPR and LLR features
    HIDDEN_UNITS = 40
    CD_K = 1
    EPOCHS = 30

    CUDA = False
    CUDA_DEVICE = 0

    if CUDA:
        torch.cuda.set_device(CUDA_DEVICE)

    # Loading dataset
    print('Loading dataset...')
    with open('../../data/l2_arctic_cache', 'r') as reader:
        files = reader.read().splitlines()
    with open('../../data/train_split', 'r') as reader:
        train_idx = reader.read().splitlines()
    train_files = [files[int(val)] for val in train_idx]
    sym_table = utterance.read_sym_table('../../data/arpa_phonemes')
    train_dataset = L2ArcticMPDset(train_files, sym_table, 'all', 'all', True)
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                               batch_size=BATCH_SIZE,
                                               shuffle=True)

    # Training RBM
    print('Training RBM...')
    rbm = RBM(VISIBLE_UNITS, HIDDEN_UNITS, CD_K, use_cuda=CUDA)
    for epoch in range(EPOCHS):
        epoch_error = 0.0
        for batch, _ in train_loader:
            batch = batch.view(len(batch), VISIBLE_UNITS).type(
                torch.FloatTensor)  # flatten input data and to float type

            if CUDA:
                batch = batch.cuda()

            batch_error = rbm.contrastive_divergence(batch)

            epoch_error += batch_error

        print('Epoch Error (epoch=%d): %.4f' % (epoch, epoch_error))

    # Save the trained model
    timestamp = datetime.datetime.fromtimestamp(time.time())
    output_dir = '../../exp/rbm_pre_training_%d%d%d-%d%d%d' % (
        timestamp.year, timestamp.month, timestamp.day, timestamp.hour,
        timestamp.minute, timestamp.second)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    print('Saving the RBM model to '+output_dir)
    with open(os.path.join(output_dir, 'rbm.pkl'), 'wb') as writer:
        pickle.dump(rbm, writer)
