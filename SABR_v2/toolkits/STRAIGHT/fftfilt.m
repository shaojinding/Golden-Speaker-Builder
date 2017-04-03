function y = fftfilt(b,x,nfft)

%not really fftfilt, but just uses filter with lower memory
%better than recoding all STRAIGHT stuff

y=filter(b,1,x);