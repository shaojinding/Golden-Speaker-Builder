function [ sucess ] = debug_model( anchor_wav_list, left_list, right_list, anchor_labels, pitch_file, save_path )
save([save_path + '/debug.mat'], 'anchor_wav_list', 'left_list', 'right_list', 'anchor_labels', 'pitch_file');
sucess = 1;
end
