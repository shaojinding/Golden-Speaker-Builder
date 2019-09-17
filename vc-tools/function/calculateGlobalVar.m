% calculateGlobalVar: calculate GVs of all the utterances in utts, used for
% building GMM model
%
% Syntax: calculateGlobalVar(utts, range)
%
% Inputs:
%   utts: list of utts
%   range: mfcc components used, default to 2:25
%
% Outputs:
%   uttGVs: GV list for all utts, n*d matrix, n is number of utts, d is
%   length of range
%
% Other m-files required: None
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: 04/28/2017; Last revision: 10/19/2018
% Revision log:
%   04/28/2017: function creation, Guanlong Zhao
%   05/10/2017: added doc, GZ
%   05/15/2017: removed hard-coded mfcc dim, GZ
%   06/26/2017: fixed input parsing bug, GZ
%   09/10/2017: added support for choosing features, GZ
%   10/19/2018: update for GSB version, GZ

function uttGVs = calculateGlobalVar(utts, range, feat)
    if nargin < 2
        range = 2:size(utts(1).mfcc, 1);
    end
    if nargin < 3
        feat = 'mfcc';
    end
    uttGVs = zeros(length(utts), length(range));
    for ii = 1:length(utts)
        uttGVs(ii, :) = var(utts(ii).(feat)(range, :)');
    end
end