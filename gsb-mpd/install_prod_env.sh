#!/usr/bin/env bash
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

# Install all dependencies for the production environment. The main difference
# between the production and develop environment is that the production server
# does not have GPU, thus requires CPU packages. Also, we have to compile
# PyTorch from source since.

# Setting
# Check for CONDA_PATH, can be set through export CONDA_PATH=`conda info --base`
# The script does not do this for you. It is the root dir of your conda install.
if [[ -z "${CONDA_PATH}" ]]; then
    echo "Must set environment variable conda root path: CONDA_PATH"
    echo "Can obtain it through conda info --base"
    exit 1
fi
echo "Setting up conda."
source ${CONDA_PATH}/etc/profile.d/conda.sh
ENV_YML_PATH=environment_prod.yml

# Install relatively easy-to-install dependencies
echo "Installing dependencies from conda."
conda env create -f ${ENV_YML_PATH}
echo "Finished installing dependencies from conda."

# Activate the env
# Name is first line, second item
ENV_NAME="$(head -n 1 ${ENV_YML_PATH} | cut -d' ' -f2)"
conda activate ${ENV_NAME}

# Compile PyTorch from source
echo "Installing PyTorch from source code."
export CMAKE_PREFIX_PATH=${CONDA_PATH}
export NO_CUDA=1
mkdir third_party
cd third_party
git clone --recursive https://github.com/pytorch/pytorch
cd pytorch/
git checkout tags/v0.4.1 -b v0.4.1
git submodule update --init
python setup.py install
cd ../../
echo "Cleaning up build files."
rm -R third_party
echo "Finished installing PyTorch from source code."

# Compile protocol buffer
echo "Compiling protocol buffer."
protoc -I=src/common --python_out=src/common src/common/data_utterance.proto
echo "Finished compiling protocol buffer."

echo "All done."


