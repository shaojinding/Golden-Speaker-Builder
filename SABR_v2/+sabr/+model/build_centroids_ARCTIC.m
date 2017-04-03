function [spkr] = build_centroids_ARCTIC(speaker, processed_dir, files)
%once we have everything preprocessed, we need to run through each
%utterance and build a distribution of the phoneme centers.

addpath('./toolkits/ARCTIC/');

arctic_phonemes;

spkr = struct('speaker_id', speaker, 'centroids',[],'f0_mean',0,'f0_std',0);

disp('Extracting centroids');

%compute centroids
for i=1:length(PHONEMES)
    samples = select_phoneme(PHONEMES{i},processed_dir, files, {'spectrum'});
    
    sample_mean = mean(samples{1},2);
    
    [v,min_idx] = min(pdist2(samples{1}', sample_mean'));
    
    disp(['min phoneme distance for ' PHONEMES{i} ' : ' num2str(v)])
    
    if(isempty(min_idx))
        spkr.centroids(:,i) = 0;
    else
        spkr.centroids(:,i) = samples{1}(:,min_idx);
    end
end

disp('Extracting pitch');

all_f0 = select_field_by(processed_dir, files, @(x) x>0, 'f0','f0');

spkr.f0_mean = trimmean(log(all_f0),25);
spkr.f0_std  = std(log(all_f0));