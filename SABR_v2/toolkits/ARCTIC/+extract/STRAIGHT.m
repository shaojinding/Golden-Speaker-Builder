function [ pitch, comp_spec, ap ] = STRAIGHT( audio, sr, window, step, compression, prmF0, prmS)
%EXTRACT_STRAIGHT Summary of this function goes here
%   audio:  waveform to extract spectrum info from
%   sr:     sampling rate of audio
%   window: window size of spectrum, in ms
%   step:   step size of spectrum, in ms

if(nargin < 7)
    prmS.defaultFrameLength     = window; %in ms
    prmS.spectralUpdateInterval = step;   %in ms
end

if(nargin < 6)
    prmF0.F0defaultWindowLength = window;
    prmF0.F0frameUpdateInterval = step; %in ms
    prmF0.F0searchLowerBound    = 50;
    prmF0.F0SearchUpperBound    = 400;
end


disp('Extracting STRAIGHT F0');
pitch    = MulticueF0v14  (audio,sr, prmF0);

disp('Extracting STRAIGHT spectrogram');
[n3sgram, prmSout]  = exstraightspec (audio,pitch,sr,prmS);

disp('Extracting STRAIGHT aperiodicity');
ap       = exstraightAPind(audio,sr,pitch,prmF0);

comp_spec = compression(n3sgram,sr);

end

