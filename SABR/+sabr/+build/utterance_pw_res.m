function [audio_h, weights, spec_hat, mfcc_hat, old_synth] = utterance_pw_res(src_spkr, tgt_spkr, audio, sr, varargin)

if(size(src_spkr.centroids,2) ~= size(tgt_spkr.centroids,2))
    error('Source and target speaker have different number of centroids.');
end

if(size(src_spkr.centroids,1) ~= size(tgt_spkr.centroids,1))
    error('Source and target speaker have different number of features.');
end

p = inputParser;

defaultSpectralUpdate = 1;
defaultFrameLength    = 80;
defaultBasis          = 2:size(src_spkr.centroids,1);
defaultLambda         = 0.025;

addRequired(p,'src_spkr');
addRequired(p,'tgt_spkr');
addRequired(p,'audio',@(x) isnumeric(x) && isvector(x));
addRequired(p,'sr',@(x) isnumeric(x) && (x>0));
addOptional(p,'lambda',defaultLambda,@isnumeric);
addOptional(p,'updateInterval',defaultSpectralUpdate,@isnumeric);
addOptional(p,'frameLength',   defaultFrameLength,   @isnumeric);
addOptional(p,'basis',defaultBasis,@(x) all(isnumeric(x) & x>0));
addOptional(p,'debug',0);
addOptional(p,'old',0);
addOptional(p,'nowarp',0);
addOptional(p,'minstep',0);
addOptional(p,'maxstep',0);

parse(p, src_spkr, tgt_spkr, audio, sr, varargin{:});

basis      = p.Results.basis;
penalty    = p.Results.lambda;
debug      = p.Results.debug;
minstep    = p.Results.minstep;

%Do we want to synthesize the old method of no residual warping?
old_method = p.Results.old;
old_synth  = [];

%do we want to not warp, too?
no_warp    = p.Results.nowarp;

%% Extract source utterance MFCCs

[ src_f0, src_spec, src_ap ] = cache.load_straight( audio, sr );

src_mfcc = spectrum.spec2mfcc(src_spec, sr, basis(end), 0);

%% Build VTLN transforms for all anchors
vtln = cell(1,(size(tgt_spkr.centroids,2)));

for anchor=1:length(vtln)
    [p,l0] = warp.optimize_warp(src_spkr.centroids(:,anchor),tgt_spkr.centroids(:,anchor));
    vtln{anchor} = warp.linear_cep(basis(end),basis(end),p,l0);
end

%% Build SABR representation and estimate target speaker spectrum
% estimate the wieghts in the context of everything but pause
weights  = sabr.build.weights(src_spkr.centroids(:,1:end-1), src_mfcc, penalty, basis);

pause_weight = zeros(1,size(src_mfcc,2));
for f=1:length(weights)
    pause_weight(f) = 1-sum(weights(1:size(tgt_spkr.centroids,2)-1,f));
end

weights = [weights; pause_weight];

tgt_est = tgt_spkr.centroids * weights;
tgt_est(1,:) = src_mfcc(1,:);

%% Estimate the residual in the context of each of the anchors, just like a GMM

res = cell(1,size(weights,1));

for anchor=1:size(weights,1)
    res{anchor} = src_mfcc - src_spkr.centroids(:,anchor);
end

warp_res = zeros(size(src_mfcc));

DCT = warp.linear_cep(basis(end),basis(end),1,1);

for a=1:size(weights,1)
    if(no_warp)
        warp_res = warp_res + repmat(weights(a,:),size(src_mfcc,1),1) .* res{a};
    else
        warp_res = warp_res + DCT'*vtln{a}*(repmat(weights(a,:),size(src_mfcc,1),1) .* res{a});
    end
end
warp_res(1,:) = 0;

mfcc_hat = tgt_est + warp_res;

%% reconstruct the audio

spec_hat = spectrum.invmfcc(mfcc_hat,sr,size(src_spec,1));
adj_f0   = vc.adj_f0(src_f0, tgt_spkr.f0_mean, tgt_spkr.f0_std);

%spec_hat = spec_hat + mfcc_residual;

if(debug)
    figure(1)
    clf;
    subplot(221);
    imagesc(log(src_spec));
    title('Source spectrum');
    subplot(222);
    imagesc(log(spectrum.invmfcc(src_mfcc,16e3,513)));
    title('Source MFCC compression');
    subplot(223);
    imagesc(log(spectrum.invmfcc([src_mfcc(1,:); tgt_spkr.centroids(basis,:) * weights],16e3,513)));
    title('Target SABR');
    subplot(224);
    imagesc(log(spectrum.invmfcc(tgt_est,16e3,513)));
    title('Target SABR + Residual');
    
    figure(2);
    subplot(211);
    imagesc(log(spectrum.invmfcc(residual_mfcc,16e3,size(src_spec,1))));
    title('Original residual');
    caxis([-3 3]);
    subplot(212);
    imagesc(log(spectrum.invmfcc(warped_residual_mfcc,16e3,size(src_spec,1))));
    title('Warped residual');
    caxis([-3 3]);
    
    figure(3);
    clf; hold on;
    plot(warp);
    plot(mean(warp'),'r--','lineWidth',3.0);
    title('SRC-TGT Warp functions');
    xlabel('SRC MFC');
    ylabel('TGT MFC');
    
    figure(4);
    clf;
    imagesc(warp * (weights ./ repmat(full(sum(weights,1)),size(weights,1),1)));
    
    figure(5);
    clf;
     PHONEMES = {'AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'B',  'CH', 'D',...
            'DH', 'EH', 'ER', 'EY', 'F', 'G', 'HH', 'IH', 'IY', 'JH',...
            'K', 'L', 'M', 'N', 'NG', 'OW', 'OY', 'P', 'R', 'S', ...
            'SH', 'T', 'TH', 'UH', 'UW', 'V', 'W', 'Y', 'Z', 'ZH', ...
            'PAU'};
    
    imagesc(weights);
    
    set(gca,'YTick',1:41)
    set(gca,'YTickLabel',PHONEMES);
    
end

%adj_ap = warp_ap(src_ap, warp, weights);

audio_h = exstraightsynth(adj_f0,spec_hat,src_ap,sr);
audio_h = audio_h ./ 2^15; %as per STRAIGHT documentation, see section 4.1

if(old_method)
    old_spec_hat = spectrum.invmfcc([src_mfcc(1:(basis(1)-1),:); tgt_spkr.centroids(basis,:) * weights],16e3,size(src_spec,1));
    old_synth = exstraightsynth(adj_f0,old_spec_hat,src_ap,sr);
    old_synth = old_synth ./ 2^15;
end

    function W = warp_speakers(src_spkr, tgt_spkr)
        W = [];
        for i=1:size(src_spkr.centroids,2)
            [~,~,W(:,i)] = sabr.residual.dfw_mfcc(src_spkr.centroids(:,i),tgt_spkr.centroids(:,i));
            %[~,~,W(:,i)] = sabr.residual.dfw_mfcc(src_spkr.centroids(:,i),tgt_spkr.centroids(:,i));
        end
    end

    function ap_warp = warp_ap(ap, warp, weights)
        %compress AP
        ap_mfcc = spectrum.spec2mfcc(-ap,16e3,basis(end),0);
        warped_ap = sabr.residual.warp_utt(warp, weights, ap_mfcc);
        ap_warp = -spectrum.invmfcc(warped_ap,16e3,size(ap,1));
    end

end