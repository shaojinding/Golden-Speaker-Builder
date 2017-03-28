function success = synthesize( source_analysis_file, source_model_file, target_model_file, synthesis_wav_output)

config;
%set up synth parameters
SR = 16e3;

%load source analysis

source_utt = load(source_analysis_file,'ap','spectrum','f0');

% load source model

load(source_model_file);

source_model = sabr_model;

% source_model.centroids(:,13) = [];
source_model.centroids(:,end)= [];

% load target model

load(target_model_file);

target_model = sabr_model;

%% Set up source variables

src_ap   = source_utt.ap;
src_f0   = source_utt.f0;
src_mfcc = source_utt.spectrum;

%% SABR synthesis

n_mfcc = size(source_utt.spectrum,1);
basis  = 2:n_mfcc;

%% Build SABR representation and estimate target speaker spectrum
% estimate the wieghts in the context of everything but pause
sabr_weights  = sabr.build.weights(source_model.centroids(:,1:end), source_utt.spectrum, 0.025, basis);

pause_weight = zeros(1,size(src_mfcc,2));
for f=1:length(sabr_weights)
    wt_l1 = sum(sabr_weights(1:size(target_model.anchors,2)-1,f));
    
    %if we can add a silence weight, we should
    if(wt_l1 < 1)
        pause_weight(f) = 1-sum(sabr_weights(1:size(target_model.anchors,2)-1,f));
    else %otherwise, we need to normalize the weight vector to 1
        pause_weight(f) = 0;
        sabr_weights(1:size(target_model.anchors,2)-1,f) = ...
            sabr_weights(1:size(target_model.anchors,2)-1,f) ./ wt_l1;
    end
end
% we probably don't need to do this since we dno't have a pause weight
%weights = [weights; pause_weight];

tgt_est = [src_mfcc(1,:); target_model.anchors(2:end,:) * sabr_weights];

% build warping between source and target models
vtln = cell(1,(size(target_model.anchors,2)));

for anchor=1:length(vtln)
    [p,l0] = warp.optimize_warp(source_model.centroids(:,anchor),target_model.anchors(:,anchor));
    vtln{anchor} = warp.linear_cep(n_mfcc,n_mfcc,p,l0);
end

%% Estimate the residual in the context of each of the anchors, just like a GMM

res = cell(1,size(sabr_weights,1));

for anchor=1:size(sabr_weights,1)
    res{anchor} = src_mfcc - source_model.centroids(:,anchor);
end

warp_res = zeros(size(src_mfcc));

DCT = warp.linear_cep(basis(end),basis(end),1,1);

for a=1:size(sabr_weights,1)
    warp_res = warp_res + DCT'*vtln{a}*(repmat(sabr_weights(a,:),size(src_mfcc,1),1) .* res{a});
end
warp_res(1,:) = 0;

mfcc_est = tgt_est + warp_res;

%% synthesize 
spec_hat = spectrum.invmfcc(mfcc_est,SR,size(src_ap,1));
% adj_f0   = vc.adj_f0(src_f0, target_model.f0_mean, target_model.f0_std);
adj_f0   = vc.adj_f0(src_f0, source_model, target_model.f0_mean, target_model.f0_std);

% STRAIGHT synthesis

audio_est = exstraightsynth(adj_f0,spec_hat,src_ap,SR);
audio_est = audio_est ./ 2^15; %as per STRAIGHT documentation, see section 4.1

audiowrite(synthesis_wav_output,audio_est,SR);

if(exist(synthesis_wav_output))
    success = 1;
else
    success = 0;
end

end
