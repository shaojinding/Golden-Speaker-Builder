function [ f0, n3sgram, ap ] = load_straight( audio, sr, varargin )
%LOAD_STRAIGHT loads the straight data if we've seen the file already.
%Files are kept in the ./tmp/ directory, filename is the md5 hash of the
%first 100 frames of audio

cache.cache_config;

p = inputParser;

defaultSpectralUpdate = 1;
defaultFrameLength    = 80;
defaultF0Upper        = 400;
defaultF0Lower        = 50;

addRequired(p,'audio',@(x) isnumeric(x) && isvector(x));
addRequired(p,'sr',@(x) isnumeric(x) && (x>0));
addOptional(p,'updateInterval',defaultSpectralUpdate,@isnumeric);
addOptional(p,'frameLength',   defaultFrameLength,   @isnumeric);
addOptional(p,'f0upper',       defaultF0Upper,       @isnumeric); 
addOptional(p,'f0lower',       defaultF0Lower,       @isnumeric);

parse(p,audio,sr,varargin{:});

spectral_update = p.Results.updateInterval;
frame_length    = p.Results.frameLength;
f0upper         = p.Results.f0upper;
f0lower         = p.Results.f0lower;

f0      = [];
n3sgram = [];
ap      = [];

name = cache.hash([frame_length spectral_update f0lower f0upper audio(100:1100)']);

if(exist([CACHE_LOCATION name '.mat'],'file'))
   disp(['Loading cached data: ' CACHE_LOCATION name '.mat']);
   load([CACHE_LOCATION name '.mat']);
   return;
end

[ f0, n3sgram, ap ] = extract.STRAIGHT( audio, sr, varargin{:});

save(['./tmp/' name '.mat'],'f0','n3sgram','ap');
end