% speechSynthesis: synthesis speech from an utterance object
%
% Syntax: utt = speechSynthesis(utt)
%
% Inputs:
%   utt: an utterance object
%
% Outputs:
%   utt: an utterance object, with synthesized speech (wav)
%
% Other m-files required: None
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: 04/18/2017; Last revision: 10/10/2018
% Revision log:
%   04/18/2017: function creation, Guanlong Zhao
%   04/20/2017: added doc, Guanlong Zhao
%   10/10/2018: added support to 'WORLD' vocoder, GZ

function utt = speechSynthesis(utt)
    switch utt.vocoder
        case 'TandemSTRAIGHTmonolithicPackage012'
            % Recover the source structure
            sourceStructure = utt.source;
            sourceStructure.samplingFrequency = utt.fs;

            % Recover the filter structure
            filterStructure = struct;
            filterStructure.spectrogramSTRAIGHT = utt.spec;

            % Synthesis wave form
            synthOut = exGeneralSTRAIGHTsynthesisR2(sourceStructure, filterStructure);
            utt.wav = synthOut.synthesisOut/max(abs(synthOut.synthesisOut))*0.8;
        case 'WORLD'
            % Recover the source structure
            sourceParameter = utt.source;

            % Recover the filter structure
            specParameters = utt.filter;
            specParameters.spectrogram = utt.spec;

            % Synthesis wave form
            utt.wav = Synthesis(sourceParameter, specParameters);
        otherwise
            error('unknow type of vocoder');
    end
end
