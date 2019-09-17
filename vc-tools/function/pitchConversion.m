% pitchConversion: a one stop function for converting pitch, now support
% pitch model built using 'log', 'heq'
%
% Syntax: pitchConversion(utt, srcPitchModel, tgtPitchModel)
%
% Inputs:
%   utt: the utterance that you want to convert
%   srcPitchModel: a pitch model for source
%   tgtPitchModel: should have the same type as the source model
%
% Outputs:
%   covUtt: pitch converted utterance
%
% Other m-files required: covertF0HEQ
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: 04/28/2017; Last revision: 10/23/2018
% Revision log:
%   04/28/2017: function creation, Guanlong Zhao
%   05/10/2017: added doc, GZ
%   07/03/2017: added mode 'hertz', GZ
%   07/19/2017: added mode 'gmm', GZ
%   10/23/2018: change to fit GSB server, GZ

function covUtt = pitchConversion(utt, srcPitchModel, tgtPitchModel)
    assert(strcmp(srcPitchModel.mode, tgtPitchModel.mode), 'Error: should use same type of pitch models');
    f0 = utt.source.f0;
    logscaling = @(x) exp((log(x+eps)-srcPitchModel.logmean)*(tgtPitchModel.logstd/srcPitchModel.logstd)+tgtPitchModel.logmean);
    
    switch srcPitchModel.mode
        case 'log'
            covF0 = logscaling(f0);
        case 'heq'
            covF0 = covertF0HEQ(f0, srcPitchModel, tgtPitchModel);
        otherwise
            error('Mode not supported!');
    end
    
    covUtt = utt;
    covUtt.source.f0 = covF0;
    if strcmp(utt.vocoder, 'TandemSTRAIGHTmonolithicPackage012')
        covUtt.source.targetF0 = min([200, max([32, min(covF0(utt.source.vuv>0))])]);
    end
end