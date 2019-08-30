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

# Run coverage report.
# You should be in the right conda environment.
TEST_PATH=`pwd`
PROJECT_PATH=${TEST_PATH}/..
export PYTHONPATH=${PROJECT_PATH}/src:$PYTHONPATH

nosetests --with-coverage --cover-erase --cover-package=../src/common \
--cover-package=../src/mpd --cover-package=../src/ppg --cover-html
