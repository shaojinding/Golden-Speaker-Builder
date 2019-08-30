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

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class ClassAwareCELoss(nn.Module):
    """
    Each output dimension corresponds to a classifier and should be trained
    using data from that class only.
    """

    def __init__(self):
        super(ClassAwareCELoss, self).__init__()

    def forward(self, y, t):
        """
        Args:
            y: A batch_size * num_dim tensor.
            t: A batch_size * 2, where dim1 is the target, and dim2 is the
            phoneme class.

        Returns:
            loss
        """
        # Valid output value for each target
        idx = t[:, 1].long().view(-1, 1)
        # For each output frame, get the dimension specified in the
        # corresponding idx number.
        y_valid = y.gather(1, idx)

        t_valid = t[:, 0].view(-1, 1)  # Ignore the phoneme label
        loss_fn = nn.BCELoss()
        loss = loss_fn(y_valid, t_valid)
        return loss


class L2ArcticFCnet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid = nn.Sigmoid()
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(0)

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid(out)
        out = self.fc2(out)
        out = self.softmax(out)
        return out


class L2ArcticFCnetJoint(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJoint, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.sigmoid2 = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid1(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        return out


class L2ArcticFCnetJointDropout(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointDropout, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.sigmoid2 = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid1(out)
        out = self.dropout(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        return out


class L2ArcticFCnetJointDropoutMultiLayer(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointDropoutMultiLayer, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.sigmoid2 = nn.Sigmoid()
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.sigmoid3 = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid1(out)
        out = self.dropout1(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        out = self.dropout2(out)
        out = self.fc3(out)
        out = self.sigmoid3(out)
        return out


class L2ArcticFCnetJointMultiLayer(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointMultiLayer, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.sigmoid2 = nn.Sigmoid()
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.sigmoid3 = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid1(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        out = self.fc3(out)
        out = self.sigmoid3(out)
        return out


class L2ArcticFCnetJointBN(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointBN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.batchnorm = nn.BatchNorm1d(hidden_size)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.sigmoid2 = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.sigmoid1(out)
        out = self.batchnorm(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        return out


class L2ArcticFCnetJointBNv2(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointBNv2, self).__init__()
        self.batchnorm1 = nn.BatchNorm1d(input_size)
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.sigmoid1 = nn.Sigmoid()
        self.batchnorm2 = nn.BatchNorm1d(hidden_size)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.sigmoid2 = nn.Sigmoid()

    def forward(self, x):
        out = self.batchnorm1(x)
        out = self.fc1(out)
        out = self.sigmoid1(out)
        out = self.batchnorm2(out)
        out = self.fc2(out)
        out = self.sigmoid2(out)
        return out


class L2ArcticFCnetJointReLU(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(L2ArcticFCnetJointReLU, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.sigmoid(out)
        return out


class L2ArcticRNNv0(nn.Module):
    def __init__(self, input_size, hidden_size, num_rnn_layers, num_output,
                 rnn_type='LSTM', dropout_rate=0, bidirectional=False,
                 use_last=True):
        """Classification model with RNN layers.

        Args:
            input_size: Input size.
            hidden_size: Hidden neuron size for the RNN layers.
            num_rnn_layers: Number of RNN layers.
            num_output: Number of output nodes.
            rnn_type: 'LSTM' or 'GRU'.
            dropout_rate: Dropout rate for RNN layer(s).
            bidirectional: Direction of the RNNs.
            use_last: bool. When performing forward, whether to use the last
            output in a sequence or the average output of a sequence.
        """
        super(L2ArcticRNNv0, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_rnn_layers = num_rnn_layers
        self.num_output = num_output
        self.rnn_type = rnn_type
        self.dropout_rate = dropout_rate
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        self.use_last = use_last

        if self.rnn_type == 'LSTM':
            self.rnn = nn.LSTM(input_size=self.input_size,
                               hidden_size=self.hidden_size,
                               num_layers=self.num_rnn_layers,
                               dropout=self.dropout_rate,
                               batch_first=True,
                               bidirectional=self.bidirectional)
        elif self.rnn_type == 'GRU':
            self.rnn = nn.GRU(input_size=self.input_size,
                              hidden_size=self.hidden_size,
                              num_layers=self.num_rnn_layers,
                              dropout=self.dropout_rate,
                              batch_first=True,
                              bidirectional=self.bidirectional)
        else:
            raise ValueError('Only support LSTM and GRU.')

        self.fc = nn.Linear(self.hidden_size*self.num_directions,
                            self.num_output)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, seq_lengths, hidden):
        """
        Args:
            x: (batch_size, seq_len, input_size)
            seq_lengths: (batch_size)
            hidden: refer to nn.LSTM and nn.GRU

        Returns:
            out: (1, batch_size)
        """
        packed_input = pack_padded_sequence(x, seq_lengths, batch_first=True)
        packed_output, hidden = self.rnn(packed_input, hidden)
        out_rnn, _ = pad_packed_sequence(packed_output, batch_first=True)

        row_indices = torch.arange(0, x.size(0)).long()
        col_indices = [val - 1 for val in seq_lengths]

        if self.use_last:
            last_tensor = out_rnn[row_indices, col_indices, :]
        else:
            # use mean
            last_tensor = out_rnn[row_indices, :, :]
            last_tensor = torch.mean(last_tensor, dim=1)

        # last_tensor: (batch, 1, num_directions*hidden_size)
        out = self.fc(last_tensor)
        out = self.sigmoid(out)
        return out

    def init_hidden(self, batch_size):
        """Generate initialization values for the RNNs.

        Args:
            batch_size: As the name suggests.

        Returns:
            Initial hidden values for LSTM or GRU.
        """
        if self.rnn_type == 'LSTM':
            return (torch.zeros(self.num_rnn_layers*self.num_directions,
                                batch_size, self.hidden_size),
                    torch.zeros(self.num_rnn_layers*self.num_directions,
                                batch_size, self.hidden_size))
        else:
            return torch.zeros(self.num_rnn_layers*self.num_directions,
                               batch_size, self.hidden_size)
