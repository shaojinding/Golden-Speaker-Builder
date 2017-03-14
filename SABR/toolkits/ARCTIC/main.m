addpath('./rastamat/');

config;

SPEAKERS = {'rgo'};

spec_method = @(x,sr) extract.STRAIGHT( x, sr, 80, 1, (@(x,sr) mfcc.straight2mfcc(x, sr, 24, 0)));

indirectory = [ARCTIC_PATH 'psi_rgo_arctic'];
outdir      = [ARCTIC_PATH 'processed/rgo/'];

for i=1:length(SPEAKERS)
    indirectory = [ARCTIC_PATH 'psi_rgo_arctic'];
    output      = [ARCTIC_PATH 'processed/rgo/'];
    
    preprocess_speaker(indirectory, output, spec_method, [], 1);
end