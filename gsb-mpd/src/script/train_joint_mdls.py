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

"""This script trains a joint MPD model for all phonemes.

Each output node is a one layer NN logistic binary classifier.
The classification is based on an universal threshold on the raw output values
of the classifiers.
"""

import datetime
import logging
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import scipy
import time
import torch
from common import utterance
from mpd.classifiers import L2ArcticFCnet, L2ArcticFCnetJoint,\
    L2ArcticFCnetJointReLU, ClassAwareCELoss, L2ArcticFCnetJointBN,\
    L2ArcticFCnetJointDropout, L2ArcticFCnetJointDropoutMultiLayer,\
    L2ArcticFCnetJointMultiLayer
from mpd.l2_aratic_mpd_dataset import L2ArcticMPDset
from sklearn.metrics import precision_recall_curve
from torch.nn.parameter import Parameter


def train_model(train_data, nn_model_type='L2ArcticFCnetJoint',
                pretrained_rbm=None):
    if nn_model_type == 'L2ArcticFCnetJoint':
        model = L2ArcticFCnetJoint(
            input_size, hidden_size, num_classes)
    elif nn_model_type == 'L2ArcticFCnetJointReLU':
        model = L2ArcticFCnetJointReLU(
            input_size, hidden_size, num_classes)
    elif nn_model_type == 'L2ArcticFCnetJointDropout':
        model = L2ArcticFCnetJointDropout(
            input_size, hidden_size, num_classes)
    elif nn_model_type == 'L2ArcticFCnetJointBN':
        model = L2ArcticFCnetJointBN(
            input_size, hidden_size, num_classes)
    elif nn_model_type == 'L2ArcticFCnetJointDropoutMultiLayer':
        model = L2ArcticFCnetJointDropoutMultiLayer(
            input_size, hidden_size, num_classes)
    elif nn_model_type == 'L2ArcticFCnetJointMultiLayer':
        model = L2ArcticFCnetJointMultiLayer(
            input_size, hidden_size, num_classes)
    else:
        raise ValueError(nn_model_type + ' is not supported.')

    if pretrained_rbm is not None:
        print('Initializing hidden layer with RBM model...')
        stdv = math.sqrt(input_size)
        scaling_factor_bias = pretrained_rbm.hidden_bias.abs().max() * stdv
        model.fc1.bias = Parameter(
            pretrained_rbm.hidden_bias/scaling_factor_bias)
        # The RBM trainer is input*output while the FC layer in PyTorch is
        # output*input
        scaling_factor_weight = pretrained_rbm.weights.abs().max() * stdv
        model.fc1.weight = Parameter(
            pretrained_rbm.weights.transpose(0, 1)/scaling_factor_weight)

    model = model.to(device)

    criterion = ClassAwareCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    total_step = len(train_data)
    for epoch in range(num_epochs):
        for i, (curr_feats, curr_labels) in enumerate(train_loader):
            if curr_feats.shape[0] < 2:
                logging.warning('Skip batch that only has one sample.')
                continue
            # Move tensors to the configured device
            curr_feats = curr_feats.type(torch.FloatTensor).to(device)
            curr_labels = curr_labels.type(torch.FloatTensor).to(device)

            # Forward pass
            curr_outputs = model(curr_feats)
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
    num_classes = 39
    num_epochs = 100
    batch_size = 128
    learning_rate = 0.001
    model_type = 'L2ArcticFCnetJoint'
    # If is_train is False, then have to provide a path with cached model files.
    is_train = True
    # Path to dir that contains pre-trained models.
    cache_dir = ''
    is_rbm = False
    # Path to pre-trained RBM model.
    # rbm_path = '../../exp/rbm_pre_training_20181119-15211/rbm.pkl'
    rbm_path = ''
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

    # Load RBM model if provided.
    if is_rbm:
        print('Loading pre-trained RBM model...')
        assert os.path.isfile(rbm_path), 'Invalid rbm file path: '+rbm_path
        with open(rbm_path, 'rb') as reader:
            rbm = pickle.load(reader)
    else:
        rbm = None

    # Train the model.
    if is_train:
        print('Loading training data...')
        train_dataset = L2ArcticMPDset(train_files, sym_table, 'all', {'s'})
        train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                                   batch_size=batch_size,
                                                   shuffle=True)
        print('Start model training...')
        mdl = train_model(train_loader, model_type, rbm)
        print('Finish model training')
        torch.save(mdl.state_dict(), os.path.join(output_dir, 'mdl.ckpt'))
    else:
        mdl = L2ArcticFCnet(
            input_size, hidden_size, num_classes).to(device)
        mdl.load_state_dict(torch.load(os.path.join(output_dir, 'mdl.ckpt')))

    f1 = None
    thresholds = None
    idx = None
    if is_test:
        # Test the model.
        # Load test data.
        print('Loading test data...')
        test_dataset = L2ArcticMPDset(test_files, sym_table,
                                      keep_phonemes='all',
                                      keep_annotations={'s'})
        test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                                  batch_size=batch_size,
                                                  shuffle=False)
        # In test phase, we don't need to compute gradients (for memory
        # efficiency).
        with torch.no_grad():
            mdl.eval()
            predicts = np.array([])
            answers = np.array([])
            for feats, labels in test_loader:
                feats = feats.type(torch.FloatTensor).to(device)
                # labels = labels[:, 0].to(device)
                outputs = np.zeros(labels.shape[0])
                for ii, phoneme_idx in enumerate(labels[:, 1]):
                    feat = feats[ii, :]
                    phoneme_idx = int(phoneme_idx.cpu())
                    outputs[ii] = mdl(feat)[phoneme_idx].cpu().numpy()
                if predicts.size > 0:
                    predicts = np.concatenate((predicts, outputs))
                else:
                    predicts = outputs
                if answers.size > 0:
                    answers = np.concatenate((answers, labels[:, 0].numpy()))
                else:
                    answers = labels[:, 0].numpy()

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
        writer.write('num_classes = %d\n' % num_classes)
        writer.write('num_epochs = %d\n' % num_epochs)
        writer.write('batch_size = %d\n' % batch_size)
        writer.write('learning_rate = %d\n' % learning_rate)
        writer.write('model_type = %s\n' % model_type)
        writer.write('is_train = %d\n' % is_train)
        writer.write('cache_dir = %s\n' % cache_dir)
        writer.write('is_rbm = %d\n' % is_rbm)
        writer.write('rbm_dir = %s\n' % rbm_path)
        writer.write('is_test = %d\n' % is_test)
        writer.write('is_train_all_all_data = %d\n' % is_train_all_all_data)
