function n3sgram = mfcc2straight(mfcc,fs,nSp)
% mfcc - MFCC caluclated from spectrogram using mfcc = dct(fbank*(log(s)));
% fs   - nyquist rate for interested badwidth. (16000 if we want the filter
% bank to be created from 0  to 8000 Hz
% nSp  - number of spectral points we want to extrapolate to from 0 to fs/2
nmel = size(mfcc,1);

% Generate filter bank
% fbank = melbankm(nmel,2*size(s,1)-1,fs);
% fbank(:,end) = []; % Function returns one more frequency bin than needed
fbank=fft2melmx(nSp*2-2,fs,nmel,1,0,fs/2,1);%dlf 10/13/10
fbank=fbank(:,1:nSp);
% mfcc was calculated using Mel -> log -> DCT
% mfcc = dct(fbank*(log(s)));

fbankConvLogSpec = idct(mfcc);
logSpec = pinv(fbank)*fbankConvLogSpec;  % least square method - 
% truncate if the logSPec value is higher than 1.
% [ii,jj] = find(logSpec>1);
% 
n3sgram = exp(logSpec);
% replace n3sgram in last mel frequency bank to zero to remove high frequency
% noise introduced by the mfcc conversion process.
[~,r] = max(fbank(end,:));
n3sgram(r:end,:) = 0;
%n3sgram(find(fbank(end,:)>0.01,1):end,:)=0;
%last_nonzero = find(fbank(end-1,:)>0,1,'last');
%n3sgram(last_nonzero:end,:)=0;


