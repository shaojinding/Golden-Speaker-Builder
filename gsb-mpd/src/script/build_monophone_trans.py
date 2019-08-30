#!/usr/bin/python
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

import sys
import re
import logging
from math import isclose
from kaldi.util.options import ParseOptions
from kaldi.util.io import xopen
from kaldi.matrix.sparse import SparseVector, SparseMatrix


def parse_transitions(trans_file):
    """Parse the transition file.

    Args:
        trans_file: Transition file path, see comment in main.

    Returns:
        reduce_map: A dict whose keys are context-independent monophones (
        without stress) and values are the pdfs that correspond to this
        monophone.
    """
    extract_pattern = re.compile(r'Transition-state (\d+): phone = (\w+) '
                                 r'hmm-state = (\d+) pdf = (\d+)')

    reduce_map = {}
    with open(trans_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Transition-state'):
                trans, phone, hmm, pdf = extract_pattern.match(line).groups()
                ci_phone = phone.split('_')[0].upper()
                ci_phone = ''.join([c for c in ci_phone if not c.isdigit()])
                pdf = int(pdf)
                if ci_phone in reduce_map:
                    reduce_map[ci_phone].append(pdf)
                else:
                    reduce_map[ci_phone] = [pdf]

    for key, val in reduce_map.items():
        val = list(set(val))  # Remove duplicates
        val.sort()
        reduce_map[key] = val

    return reduce_map


if __name__ == '__main__':
    usage = """Create a transform matrix that can reduce the dimensionality of
    the full PPG to monophones.
    
    The input file is the output of the following command,
        show-transitions phone.txt final.mdl
    And the output is a d*D sparse matrix T that can map the full PPG to
    monophone PPGs, where d is the number of monophones, and D is the dimension
    of the full PPG. Each row corresponds to a monophone, and only the 
    dimensions that belong to this monophone will be set to 1. As a result, 
    the mapping from the full PPG P to the monophone PPG p is p=PT'
    
    Also output the list of monophones.
    
    Usage: python build_monophone_trans.py <trans-txt> \\ 
    <matrix-out-wspecifier> <symbol-list-txt>
    
    e.g., python build_monophone_trans.py data/trans.txt data/reduce_dim.mat \\
    data/monophones.txt
    """
    logging.getLogger().setLevel(logging.INFO)

    po = ParseOptions(usage)
    opts = po.parse_args()

    if po.num_args() != 3:
        po.print_usage()
        sys.exit(1)

    trans_file_path = po.get_arg(1)
    matrix_file_path = po.get_arg(2)
    monophone_file_path = po.get_arg(3)

    reduce_map = parse_transitions(trans_file_path)

    # Merge SIL and SPN
    sil_phone_idx = reduce_map.pop("SIL")
    if "SPN" in reduce_map:
        spn_phone_idx = reduce_map.pop("SPN")
        sil_phone_idx += spn_phone_idx
    sil_phone_idx = list(set(sil_phone_idx))
    sil_phone_idx.sort()

    # Figure out real phonemes
    phones = list(reduce_map.keys())
    phones.sort()

    # Append SIL to the end
    phones.append("SIL")
    reduce_map["SIL"] = sil_phone_idx
    num_phones = len(phones)
    logging.info("Number of phonemes is %d." % num_phones)
    logging.info("Phonemes are %s." % phones)

    with open(monophone_file_path, 'w') as f:
        for phone in phones:
            f.write('%s\n' % phone)

    # Figure out the maximum PPG dim
    num_pdfs = max([max(val) for val in reduce_map.values()]) + 1
    logging.info("Number of pdfs is %d." % num_pdfs)

    # This is the output matrix
    reduce_dim_mat = SparseMatrix.from_dims(num_phones, num_pdfs)
    for ii, phone in enumerate(phones):
        # For each rwo, set the non-zero elements
        valid_pairs = [(int(val), 1.0) for val in reduce_map[phone]]
        curr_vec = SparseVector.from_pairs(num_pdfs, valid_pairs)
        reduce_dim_mat.set_row_(ii, curr_vec)

    # Sanity check
    sum_mat = reduce_dim_mat.sum()
    logging.info("Number of valid matrix elements is %d", sum_mat)
    assert isclose(sum_mat, num_pdfs), "The output matrix is wrong! The sum " \
                                       "of the matrix is %f but expected to " \
                                       "be %d." % (sum_mat, num_pdfs)

    with xopen(matrix_file_path, "w") as writer:
        reduce_dim_mat.write(writer.stream(), True)
        writer.flush()
