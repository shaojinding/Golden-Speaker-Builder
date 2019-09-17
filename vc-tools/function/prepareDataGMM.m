% prepareDataGMM: prepare data that are ready for the GMM training to use.
%
% Syntax: [mcep, post] = prepareDataGMM(utts)
%
% Inputs:
%   utts: A struct array. Containing utt structs.
%
% Outputs:
%   mcep: A D1*T matrix. All mceps from the utts concatenated, with mcep_0
%   and silence removed and delta features appended
%   post: A D2*T matrix. All mceps from the utts concatenated, with silence
%   removed
%
% Other m-files required: getDerivatives
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: 10/19/2018; Last revision: 10/19/2018
% Revision log:
%   10/19/2018: function creation, Guanlong Zhao

function [mcep, post] = prepareDataGMM(utts)
    numUtts = length(utts);
    % Compile training data, validate, filter silence
    mcep = [];
    post = [];
    for ii = 1:numUtts
        lab = utts(ii).lab;
        keepIdx = ~isnan(lab);
        % Get delta features for mcep
        tempmcep = getDerivatives(utts(ii).mcep(2:end, :), 1);
        % Remove silence segment
        tempmcep = tempmcep(:, keepIdx);
        mcep = [mcep, tempmcep];
        % Get posteriorgram and remove silence frames accordingly
        temppost = utts(ii).post(:, keepIdx);
        post = [post, temppost];
    end
end