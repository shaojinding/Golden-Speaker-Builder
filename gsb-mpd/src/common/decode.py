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

"""This module provides handy functions for Kaldi-decoding related tasks
"""

from kaldi import nnet3
from kaldi.util.io import xopen


def read_nnet3_model(model_path: str) -> nnet3.Nnet:
    """Read in a nnet3 model in raw format.

    Actually if this model is not a raw format it will still work, but this is
    not an official feature; it was due to some kaldi internal code.

    Args:
        model_path: Path to a raw nnet3 model, e.g., "data/final.raw"

    Returns:
        nnet: A neural network AM.
    """
    nnet = nnet3.Nnet()
    with xopen(model_path) as istream:
        nnet.read(istream.stream(), istream.binary)
    return nnet
