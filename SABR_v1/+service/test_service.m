
wav_list = dir('D:/db/ARCTIC/cmu_us_bdl_arctic/wav/arctic_a001*.wav');

wav_files = {};

for i=1:length(wav_list); wav_files{i} = [wav_list(i).folder '\' wav_list(i).name]; end;

phonemes = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'};

success = service.build_sabr_model(wav_files, ones(1,10), ones(1,10)+0.05, phonemes, wav_files{1}, '.\test_out.mat');