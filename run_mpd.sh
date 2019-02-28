#!/usr/bin/env bash
# Copyright 2018 Shaojin Ding

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Install all dependencies for the production environment. The main difference
# between the production and develop environment is that the production server
# does not have GPU, thus requires CPU packages. Also, we have to compile
# PyTorch from source since.

# Setting
# Check for CONDA_PATH, can be set through export CONDA_PATH=`conda info --base`
# The script does not do this for you. It is the root dir of your conda install.

wav_dir=$1
trans_dir=$2
save_dir=$3

if [[ -z "${CONDA_PATH}" ]]; then
    echo "Must set environment variable conda root path: CONDA_PATH"
    echo "Can obtain it through conda info --base"
    exit 1
fi
echo "Setting up conda."
source ${CONDA_PATH}/etc/profile.d/conda.sh

echo "Activate conda env"
conda activate gsb-mpd-prod

# Include the package in the python search path
PROJECT_PATH=/home/burning/Project/golden-speaker/gsb-mpd
export PYTHONPATH=${PROJECT_PATH}/src:$PYTHONPATH

mkdir -p gsb-mpd/exp/temp
python gsb-mpd/src/script/runtime_mpd_demo.py ${wav_dir} ${trans_dir} ${save_dir}

echo "All done."


