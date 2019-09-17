% Prepare test data for model building
clear
clc
rootDir = '/var/gzhao/test_data';
%% Source speaker data
recordings = dir('/var/gzhao/test_data/src/recordings/*.wav');
numWavs = length(recordings);
wavList = cell(numWavs, 1);
for ii = 1:numWavs
    wavList{ii} = fullfile(rootDir, 'src/recordings', recordings(ii).name);
end
transFile = '/var/gzhao/test_data/src/prompts.txt';
matList = dataPrep(wavList, transFile, 'BatchTag', 'cache',...
    'NumWorkers', 8, 'DataRoot', '/var/gzhao/test_data/src');

%% target speaker data
recordings = dir('/var/gzhao/test_data/tgt/recordings/*.wav');
numWavs = length(recordings);
wavList = cell(numWavs, 1);
for ii = 1:numWavs
    wavList{ii} = fullfile(rootDir, 'tgt/recordings', recordings(ii).name);
end
transFile = '/var/gzhao/test_data/tgt/prompts.txt';
matList = dataPrep(wavList, transFile, 'BatchTag', 'cache',...
    'NumWorkers', 8, 'DataRoot', '/var/gzhao/test_data/tgt');