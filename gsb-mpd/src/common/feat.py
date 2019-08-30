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

"""This module provides handy functions to perform Kaldi-related feature
operations.
"""

import logging
from kaldi.feat.mfcc import Mfcc, MfccOptions
from kaldi.feat.wave import WaveData
from kaldi.matrix import Vector, Matrix
from kaldi.matrix.common import MatrixTransposeType
from kaldi.matrix.sparse import SparseMatrix
from kaldi.util.io import xopen
import wavio


def read_wav_kaldi_internal(wav, fs) -> WaveData:
    """Internal function for converting wave data to Kaldi format.

    This function will only keep the first channel.

    Args:
        wav: S*C ndarray. S is number of samples and C is number of channels.
        fs: Sampling frequency.

    Returns:
        wd: A Kaldi-readable WaveData object.
    """
    # Only keep the first channel if more than one
    if wav.ndim >= 2:
        wav = wav[:, 0]

    # Save to a Kaldi matrix, per Kaldi's requirement.
    wav_kaldi = Matrix(1, len(wav))
    wav_kaldi.copy_rows_from_vec_(Vector(wav))

    if hasattr(WaveData, 'new'):
        wd = WaveData.new(fs, wav_kaldi)
    elif hasattr(WaveData, 'from_data'):
        wd = WaveData.from_data(fs, wav_kaldi)
    else:
        wd = None
        logging.error('Unknown Pykaldi package.')
    return wd


def read_wav_kaldi(wav_file_path: str) -> WaveData:
    """Read a given wave file to a Kaldi readable format.

    Args:
        wav_file_path: Path to a .wav file.
    Returns:
        wd: A Kaldi-readable WaveData object.
    """
    # Read in as np array not memmap.
    wavio_obj = wavio.read(wav_file_path)
    fs = wavio_obj.rate
    wav = wavio_obj.data

    wd = read_wav_kaldi_internal(wav, fs)
    return wd


def compute_mfcc_feats(wav: WaveData, mfcc_opts: MfccOptions) -> Matrix:
    """Compute MFCC features given a Kaldi WaveData.

    Args:
        wav: A WaveData object.
        mfcc_opts: An MfccOptions object containing feature extraction options.
        A few notable options are,
        - use_energy: Generally I will use False, since the energy does not
        contain much linguistic information
        - frame_opts.allow_downsample: Generally I will set this to True, since
        the AM I use can only handle the default sampling frequency (16KHz)
        - frame_opts.frame_shift_ms: For speech synthesis purposes, might be
        good to have a smaller shift (e.g., 5ms)
        - frame_opts.snip_edges: Generally I will set this to False, just to
        have a deterministic way to compute the number of frames

    Returns:
        feats: A T*D MFCC feature matrix.
    """
    mfcc = Mfcc(mfcc_opts)
    vtln_warp = 1.0  # This is the default value
    channel = 0  # Only use the first channel

    feats = mfcc.compute_features(wav.data()[channel], wav.samp_freq, vtln_warp)
    return feats


def apply_cepstral_mean_norm(feats: Matrix) -> Matrix:
    """Apply cepstral mean normalization to MFCCs.

    Note that this function does not do variance normalization, which is enough
    for GZ's purposes.

    Args:
        feats: A T*D MFCC features.

    Returns:
        feats: A T*D Normalized MFCCs.
    """
    mean = Vector(feats.num_cols)
    mean.add_row_sum_mat_(1.0, feats)
    mean.scale_(1.0 / feats.num_rows)
    for i in range(feats.num_rows):
        feats[i].add_vec_(-1.0, mean)
    return feats


def apply_lda_transform(feats: Matrix, transform: Matrix) -> Matrix:
    """Apply an LDA transform on the input features.

    The transform is a simple matrix multiplication: F = FT' (' is transpose).
    This function is an extremely simplified version of
    https://github.com/kaldi-asr/kaldi/blob/5.3/src/featbin/transform-feats.cc

    Args:
        feats: A T*D feature matrix.
        transform: A D'*D matrix, where D' is the output feature dim.

    Returns:
        feats_out: A T*D' matrix.
    """
    feat_dim = feats.num_cols
    transform_rows = transform.num_rows
    transform_cols = transform.num_cols

    if transform_cols == feat_dim:
        feats_out = Matrix(feats.num_rows, transform_rows)
        feats_out.add_mat_mat_(feats, transform, MatrixTransposeType.NO_TRANS,
                               MatrixTransposeType.TRANS, 1.0, 0.0)
    else:
        logging.error(("Transform matrix has bad dimension %dx%d versus feat "
                       "dim %d") % (transform_rows, transform_cols, feat_dim))
    return feats_out


def read_sparse_mat(sparse_mat_dir: str) -> SparseMatrix:
    """Read in a sparse matrix.

    Args:
        sparse_mat_dir: Path to the sparse matrix file.

    Returns:
        mat: A sparse matrix.
    """
    with xopen(sparse_mat_dir, 'r') as reader:
        mat = SparseMatrix()
        mat.read_(reader.stream(), reader.binary)
    return mat
