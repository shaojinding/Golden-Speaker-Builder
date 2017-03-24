function [ spec, f0, ap ] = WORLD( x, fs, compression_method)

addpath('./WORLD');

if(isempty(compression_method))
    compression_method = @(x,y) x;
end

f0_parameter = Dio(x, fs);
f0_parameter.f0 = StoneMask(x, fs,...
  f0_parameter.temporal_positions, f0_parameter.f0);

spectrum_parameter = CheapTrick(x, fs, f0_parameter);
source_parameter = D4C(x, fs, f0_parameter);

spec = compression_method(spectrum_parameter.spectrogram,fs);
f0   = source_parameter.f0;
ap   = compression_method(source_parameter.aperiodicity,fs);

end

