function [ pitch, comp_spec, ap ] = STRAIGHT( audio, sr, varargin)
%EXTRACT_STRAIGHT Summary of this function goes here
%   audio:  waveform to extract spectrum info from
%   sr:     sampling rate of audio
%   window: window size of spectrum, in ms
%   step:   step size of spectrum, in ms

p = inputParser;

defaultSpectralUpdate = 1;
defaultFrameLength    = 80;
defaultF0Upper        = 400;
defaultF0Lower        = 50;
defaultCompression    = [];

addRequired(p,'audio',@(x) isnumeric(x) && isvector(x));
addRequired(p,'sr',@(x) isnumeric(x) && (x>0));
addOptional(p,'updateInterval',defaultSpectralUpdate,@isnumeric);
addOptional(p,'frameLength',   defaultFrameLength,   @isnumeric);
addOptional(p,'f0upper',       defaultF0Upper,       @isnumeric); 
addOptional(p,'f0lower',       defaultF0Lower,       @isnumeric);
addOptional(p,'compression',   defaultCompression,   @(x) strcmpi(class(x),'function_handle'));

parse(p,audio,sr,varargin{:});

spectral_update = p.Results.updateInterval;
frame_length    = p.Results.frameLength;
f0upper         = p.Results.f0upper;
f0lower         = p.Results.f0lower;
compression     = p.Results.compression;

prmP.defaultFrameLength     = frame_length;
prmP.spectralUpdateInterval = spectral_update; %in milliseconds

prmF0.F0defaultWindowLength = frame_length;
prmF0.F0frameUpdateInterval = spectral_update; %in milliseconds
prmF0.F0searchLowerBound    = f0lower;
prmF0.F0SearchUpperBound    = f0upper;


disp('Extracting STRAIGHT F0');
pitch    = MulticueF0v14  (audio,sr, prmF0);

disp('Extracting STRAIGHT spectrogram');
n3sgram  = exstraightspec (audio,pitch,sr,prmP);

disp('Extracting STRAIGHT aperiodicity');
ap       = exstraightAPind(audio,sr,pitch,prmF0);

if(~isempty(compression))
    comp_spec = compression(n3sgram,sr);
else
    comp_spec = n3sgram;
end

end

