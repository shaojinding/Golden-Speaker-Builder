% Add dependencies for PPG-GMM
addpath /var/gzhao/SpeechToolkitPSI/acoust_based
addpath /var/gzhao/SpeechToolkitPSI/GMM
addpath /var/gzhao/SpeechToolkitPSI/kaldi2matlab
addpath /var/gzhao/SpeechToolkitPSI/netlab
addpath /var/gzhao/SpeechToolkitPSI/mcep-sptk-matlab
addpath /var/gzhao/SpeechToolkitPSI/mPraat
addpath /var/gzhao/SpeechToolkitPSI/rastamat
addpath /var/gzhao/SpeechToolkitPSI/STRAIGHTV40_007c
addpath /var/gzhao/SpeechToolkitPSI/TandemSTRAIGHTmonolithicPackage012
addpath /var/gzhao/SpeechToolkitPSI/world-0.2.3_matlab
addpath /var/gzhao/f0_heq
addpath /var/gzhao/vc-tools/function
addpath /var/gzhao/vc-tools/script
addpath /var/gzhao/vc-tools/test

% Kaldi uses this C++ library
setenv('LD_PRELOAD', '/usr/lib64/libstdc++.so.6')