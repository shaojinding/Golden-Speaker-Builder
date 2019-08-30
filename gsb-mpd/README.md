# GSB MPD

**Test coverage: `88%`**

Mispronunciation detection (MPD) based on neural network logistic classifiers for GSB.

### Install

This installation process has only been tested on **Ubuntu 16.04** and **CentOS 7.5**.

#### Download the source code

```bash
git clone https://github.tamu.edu/guanlong-zhao/gsb-mpd.git
cd gsb-mpd
```

#### Install aligner

Install a modified version of the [Montreal aligner](https://github.tamu.edu/guanlong-zhao/montreal-forced-aligner/tree/gsb-mpd) from [source](https://github.tamu.edu/guanlong-zhao/montreal-forced-aligner/blob/gsb-mpd/docs/source/installation.rst#building-from-source). Intalling the aligner from source requires that you have a working Kaldi installation. 
Then, put the compiled aligner binary, AM, and [lexicon](https://github.tamu.edu/dshj940428/SpeechToolkitPSI/blob/master/montreal-forced-aligner_v1.0/pretrained_models/dictionary) to where `src/common/align.py:MontrealAligner` specifies.

#### Install anaconda (optional)

Install [miniconda/anaconda](https://www.anaconda.com/download/) if you have not done so.

#### Setup environment

```bash
# Tell the installer where your conda is
export CONDA_PATH=`conda info --base`

# Install development environment (requires GPU support)
./install_dev_env.sh

# Install production environment (requires CPU only)
./install_prod_env.sh
```

#### Activate environment

```bash
# For dev environment
conda activate gsb-mpd-dev

# For prod environment
conda activate gsb-mpd-prod

# Include the package in the python search path
PROJECT_PATH=`pwd`
export PYTHONPATH=${PROJECT_PATH}/src:$PYTHONPATH
```

### Run unit tests

```bash
cd test
./run_coverage.sh
```

The test coverage report will be saved to `test/cover`. If all tests passed then the installation is successful.

### Run MPD
See `src/script/runtime_mpd_demo.py` for a demo.

```bash
mkdir -p exp/temp
cd src/script
python runtime_mpd_demo.py ../../test/data/test_mono_channel.wav \
    ../../test/data/test_mono_channel.txt ../../exp/temp/test.TextGrid
```