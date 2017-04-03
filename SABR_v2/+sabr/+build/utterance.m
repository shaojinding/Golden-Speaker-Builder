function [audio_h, w_out, spec_hat, mfcc_hat] = utterance(src_spkr, tgt_spkr, audio, sr, varargin)

if(size(src_spkr.centroids,2) ~= size(tgt_spkr.centroids,2))
    error('Source and target speaker have different number of centroids.');
end

if(size(src_spkr.centroids,1) ~= size(tgt_spkr.centroids,1))
    error('Source and target speaker have different number of features.');
end

p = inputParser;

defaultSpectralUpdate = 1;
defaultFrameLength    = 80;
defaultBasis          = 2:24;
defaultLambda         = 0.025;

addRequired(p,'src_spkr');
addRequired(p,'tgt_spkr');
addRequired(p,'audio',@(x) isnumeric(x) && isvector(x));
addRequired(p,'sr',@(x) isnumeric(x) && (x>0));
addOptional(p,'lambda',defaultLambda,@isnumeric);
addOptional(p,'updateInterval',defaultSpectralUpdate,@isnumeric);
addOptional(p,'frameLength',   defaultFrameLength,   @isnumeric);
addOptional(p,'basis',defaultBasis,@(x) all(isnumeric(x) & x>0));

parse(p, src_spkr, tgt_spkr, audio, sr, varargin{:});

basis          = p.Results.basis;
penalty        = p.Results.lambda;
updateInterval = p.Results.updateInterval;
frameLength    = p.Results.frameLength;

%% Extract source utterance MFCCs

[ src_f0, src_spec, src_ap ] = cache.load_straight( audio, sr, 'updateInterval', updateInterval, 'frameLength', frameLength );

src_mfcc = spectrum.spec2mfcc(src_spec, sr, basis(end), 0);

%% Build SABR representation and estimate target speaker spectrum

w_out    = sabr.build.weights(src_spkr.centroids, src_mfcc, penalty, basis);
mfcc_hat = [src_mfcc(1,:); tgt_spkr.centroids(basis,:) * w_out];
spec_hat = spectrum.invmfcc(mfcc_hat(1:24,:),sr,size(src_spec,1));
adj_f0   = vc.adj_f0(src_f0, tgt_spkr.f0_mean, tgt_spkr.f0_std);

%% reconstruct the audio

audio_h = exstraightsynth(adj_f0,spec_hat,src_ap,sr);
audio_h = audio_h ./ 2^15; %as per STRAIGHT documentation, see section 4.1