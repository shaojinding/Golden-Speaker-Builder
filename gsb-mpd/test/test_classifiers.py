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
import torch
from mpd import classifiers


class TestClassifiers(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ClassAwareCELoss(self):
        y = torch.Tensor([[0, 1, 0], [1, 0, 1], [0, 1, 1]])
        t = torch.Tensor([[0, 0], [0, 1], [1, 2]])
        loss_fn = classifiers.ClassAwareCELoss()
        loss = loss_fn(y, t)
        self.assertTrue(loss == 0)

    def test_L2ArcticFCnet(self):
        model = classifiers.L2ArcticFCnet(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticFCnetJoint(self):
        model = classifiers.L2ArcticFCnetJoint(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticFCnetJointDropout(self):
        model = classifiers.L2ArcticFCnetJointDropout(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticFCnetJointDropoutMultiLayer(self):
        model = classifiers.L2ArcticFCnetJointDropoutMultiLayer(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticFCnetJointMultiLayer(self):
        model = classifiers.L2ArcticFCnetJointMultiLayer(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticFCnetJointBN(self):
        model = classifiers.L2ArcticFCnetJointBN(10, 10, 2)
        model(torch.randn((4, 10)))

    def test_L2ArcticFCnetJointBNv2(self):
        model = classifiers.L2ArcticFCnetJointBNv2(10, 10, 2)
        model(torch.randn((4, 10)))

    def test_L2ArcticFCnetJointReLU(self):
        model = classifiers.L2ArcticFCnetJointReLU(10, 10, 2)
        model(torch.randn((1, 10)))

    def test_L2ArcticRNNv0_LSTM(self):
        x = torch.randn((4, 18, 10))
        seqlen = [18, 17, 16, 15]

        # Use last
        model = classifiers.L2ArcticRNNv0(10, 10, 2, 2, 'LSTM', 0.5, True, True)
        hidden = model.init_hidden(4)
        model(x, seqlen, hidden)

        # Use average
        model = classifiers.L2ArcticRNNv0(10, 10, 2, 2, 'LSTM', 0.5, True,
                                          False)
        hidden = model.init_hidden(4)
        model(x, seqlen, hidden)

    def test_L2ArcticRNNv0_GRU(self):
        x = torch.randn((4, 18, 10))
        seqlen = [18, 17, 16, 15]

        # Use last
        model = classifiers.L2ArcticRNNv0(10, 10, 2, 2, 'GRU', 0.5, True, True)
        hidden = model.init_hidden(4)
        model(x, seqlen, hidden)

        # Use average
        model = classifiers.L2ArcticRNNv0(10, 10, 2, 2, 'GRU', 0.5, True,
                                          False)
        hidden = model.init_hidden(4)
        model(x, seqlen, hidden)
