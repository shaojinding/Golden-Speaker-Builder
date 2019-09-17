% phones2numeric: convert phone labels in an utt struct to a numeric array
%
% Syntax: lab = phones2numeric(utt)
%
% Inputs:
%   utt: an utt struct
%
% Outputs:
%   lab: phoneme label in the form of a numeric array, 1*T vector
%
% Other m-files required: None
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: 04/26/2017; Last revision: 04/26/2017
% Revision log:
%   04/26/2017: function creation, Guanlong Zhao

function lab = phones2numeric(utt)
    uniqPhLbls = {'aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'b', 'ch', 'd', 'dh', ...
        'eh', 'er', 'ey', 'f', 'g', 'hh', 'ih', 'iy', 'jh', 'k', 'l', 'm', ...
        'n', 'ng', 'ow', 'oy', 'p', 'r', 's', 'sh', 't', 'th', 'uh', 'uw', ...
        'v', 'w', 'y', 'z', 'zh'};
    
    lab = NaN(1, size(utt.spec, 2));
    for ii = 1:length(utt.phones.phones)
        if ~isempty(utt.phones.phones{ii})
            thisPhoneLabelID = find(ismember(uniqPhLbls, utt.phones.phones{ii}));
            if ~isempty(thisPhoneLabelID)
                lab(utt.phones.startTime(ii):utt.phones.endTime(ii)) = thisPhoneLabelID;
            end
        end
    end
end