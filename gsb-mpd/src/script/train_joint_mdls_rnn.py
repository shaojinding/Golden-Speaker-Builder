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

"""This script trains a joint MPD model for all phonemes using RNNs.

Each output node is a NN logistic binary classifier.
The classification is based on an universal threshold on the raw output values
of the classifiers.
"""

import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
import time
import torch
from common import utterance
from mpd.classifiers import L2ArcticRNNv0, ClassAwareCELoss
from mpd.l2_aratic_mpd_dataset import L2ArcticMPDsetSeq, sequence_collate
from sklearn.metrics import precision_recall_curve


def train_model(train_data, nn_model_type='L2ArcticRNNv0'):
    if nn_model_type == 'L2ArcticRNNv0':
        model = L2ArcticRNNv0(input_size, hidden_size, num_rnn_layers,
                              num_classes, rnn_type, dropout_rate,
                              bidirectional, use_last)
    else:
        raise ValueError(nn_model_type+' is not supported.')

    model = model.to(device)

    criterion = ClassAwareCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    total_step = len(train_data)
    for epoch in range(num_epochs):
        for i, (curr_feats, curr_labels, curr_len) in enumerate(train_loader):
            # Move tensors to the configured device
            curr_feats = curr_feats.type(torch.FloatTensor).to(device)
            curr_labels = curr_labels.type(torch.FloatTensor).view(
                batch_size, -1).to(device)

            # Forward pass
            hidden = model.init_hidden(batch_size)
            if rnn_type == 'LSTM':
                hidden = (hidden[0].to(device), hidden[1].to(device))
            else:
                hidden = hidden.to(device)
            curr_outputs = model(curr_feats, curr_len, hidden)
            curr_outputs = curr_outputs.view(batch_size, -1)
            loss = criterion(curr_outputs, curr_labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i + 1) % 10 == 0:
                print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                      .format(epoch + 1, num_epochs, i + 1, total_step,
                              loss.item()))
    return model


if __name__ == '__main__':
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Setting
    input_size = 80
    hidden_size = 40
    num_rnn_layers = 2
    num_classes = 39
    rnn_type = 'LSTM'
    dropout_rate = 0.5
    bidirectional = True
    use_last = False
    num_epochs = 100
    batch_size = 128
    learning_rate = 0.001
    model_type = 'L2ArcticRNNv0'
    # If is_train is False, then have to provide a path with cached model files.
    is_train = True
    # Path to dir that contains pre-trained models.
    cache_dir = ''
    is_test = False
    is_train_all_all_data = True

    # Prepare data split.
    with open('../../data/l2_arctic_cache', 'r') as reader:
        files = reader.read().splitlines()
    if is_train_all_all_data:
        train_files = files
        test_files = []
        is_test = False  # There is no need to test in this case.
    else:
        with open('../../data/train_split', 'r') as reader:
            train_idx = reader.read().splitlines()
        train_files = [files[int(val)] for val in train_idx]
        with open('../../data/test_split', 'r') as reader:
            test_idx = reader.read().splitlines()
        test_files = [files[int(val)] for val in test_idx]
    sym_table = utterance.read_sym_table('../../data/arpa_phonemes')

    # Prepare output dir.
    if is_train:
        timestamp = datetime.datetime.fromtimestamp(time.time())
        output_dir = '../../exp/joint_classifiers_%04d%02d%02d-%02d%02d%02d' % (
            timestamp.year, timestamp.month, timestamp.day, timestamp.hour,
            timestamp.minute, timestamp.second)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        print('Set up output dir to '+output_dir)
    else:
        output_dir = cache_dir
        assert os.path.isdir(output_dir), 'Invalid cache dir path: '+cache_dir

    # Train the model.
    if is_train:
        print('Loading training data...')
        train_dataset = L2ArcticMPDsetSeq(train_files, sym_table, 'all', {'s'})
        train_loader = torch.utils.data.DataLoader(
            dataset=train_dataset, batch_size=batch_size, shuffle=True,
            collate_fn=sequence_collate, drop_last=True)
        print('Start model training...')
        mdl = train_model(train_loader, model_type)
        print('Finish model training')
        torch.save(mdl.state_dict(), os.path.join(output_dir, 'mdl.ckpt'))
    else:
        mdl = L2ArcticRNNv0(input_size, hidden_size, num_rnn_layers,
                            num_classes, rnn_type, dropout_rate,
                            bidirectional, use_last).to(device)
        mdl.load_state_dict(torch.load(os.path.join(output_dir, 'mdl.ckpt')))

    f1 = None
    thresholds = None
    idx = None
    if is_test:
        # Test the model.
        # Load test data.
        print('Loading test data...')
        test_dataset = L2ArcticMPDsetSeq(test_files, sym_table,
                                         keep_phonemes='all',
                                         keep_annotations={'s'})
        test_loader = torch.utils.data.DataLoader(
            dataset=test_dataset, batch_size=1, shuffle=False,
            collate_fn=sequence_collate, drop_last=False)

        # In test phase, we don't need to compute gradients (for memory
        # efficiency).
        with torch.no_grad():
            mdl.eval()
            predicts = np.array([])
            answers = np.array([])
            num_samples = len(test_loader)
            num_scored = 0
            for feats, labels, seqlen in test_loader:
                feats = feats.type(torch.FloatTensor).to(device)
                phoneme_idx = labels[0, 0, 1]
                hidden = mdl.init_hidden(1)
                if rnn_type == 'LSTM':
                    hidden = (hidden[0].to(device), hidden[1].to(device))
                else:
                    hidden = hidden.to(device)
                outputs = mdl(feats, torch.LongTensor(seqlen),
                              hidden)[0, phoneme_idx].cpu().numpy()

                predicts = np.append(predicts, outputs)
                answers = np.append(answers, labels[0, 0, 0].numpy())
                num_scored += 1
                if num_scored % 100 == 0:
                    print('%3.2f%% done.' % (100*num_scored / num_samples))

            # Data analysis part.
            precision, recall, thresholds = precision_recall_curve(
                answers, predicts)
            # Get F1 score when precision==recall.
            diff = abs(precision - recall)
            idx = diff.argmin()
            f1 = 100*2*precision[idx]*recall[idx]/(precision[idx]+recall[idx])
            print('F1 is %2.1f' % f1)
            print('Threshold is %1.2f' % thresholds[idx])
            plt.plot(precision, recall)
            plt.xlabel('Precision')
            plt.ylabel('Recall')
            print('Saving precision-recall curve...')
            plt.savefig(os.path.join(output_dir, 'pr_curve.pdf'), dpi=600)
            print('Saving analysis data to a mat file...')
            scipy.io.savemat(os.path.join(output_dir, 'analysis.mat'),
                             {'predicts': predicts, 'answers': answers,
                              'precision': precision, 'recall': recall,
                              'threshold': thresholds, 'f1': f1, 'f1_idx': idx})

    with open(os.path.join(output_dir, 'README'), 'w') as writer:
        if f1 is not None:
            writer.write('F1 is %2.1f\n' % f1)
        if thresholds is not None and idx is not None:
            writer.write('Threshold is %1.2f\n\n' % thresholds[idx])
        writer.write('input_size = %d\n' % input_size)
        writer.write('hidden_size = %d\n' % hidden_size)
        writer.write('num_rnn_layers = %d\n' % num_rnn_layers)
        writer.write('num_classes = %d\n' % num_classes)
        writer.write('rnn_type = %s\n' % rnn_type)
        writer.write('dropout_rate = %d\n' % dropout_rate)
        writer.write('bidirectional = %d\n' % bidirectional)
        writer.write('use_last = %d\n' % use_last)
        writer.write('num_epochs = %d\n' % num_epochs)
        writer.write('batch_size = %d\n' % batch_size)
        writer.write('learning_rate = %d\n' % learning_rate)
        writer.write('model_type = %s\n' % model_type)
        writer.write('is_train = %d\n' % is_train)
        writer.write('cache_dir = %s\n' % cache_dir)
        writer.write('is_test = %d\n' % is_test)
        writer.write('is_train_all_all_data = %d\n' % is_train_all_all_data)
