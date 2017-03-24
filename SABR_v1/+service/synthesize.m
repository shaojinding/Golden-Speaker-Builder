function success = synthesize( source_analysis_file, source_model_file, target_model_file, synthesis_wav_output)
config;
%set up synth parameters
SR = 16e3;

%load source analysis

source_utt = load(source_analysis_file,'ap','spectrum','f0');

% load source model

load(source_model_file);

source_model = sabr_model;

% load target model

load(target_model_file);

target_model = sabr_model;

%% Set up source variables

src_ap = source_utt.ap;
src_f0 = source_utt.f0;

%% SABR synthesis

n_mfcc = size(source_utt.spectrum,1);

% get SABR representation
sabr_weights = sabr.build.weights(source_model.centroids, source_utt.spectrum, 0.025, 2:n_mfcc);

sabr_weights(13, :) = [];

sabr_weights(end, :) = [];

% synthesize 
src_mfcc = source_utt.spectrum;

mfcc_est = [src_mfcc(1,:); target_model.anchors(2:end,:) * sabr_weights];
spec_hat = spectrum.invmfcc(mfcc_est,SR,size(src_ap,1));
adj_f0   = vc.adj_f0(src_f0, target_model.f0_mean, target_model.f0_std);

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
