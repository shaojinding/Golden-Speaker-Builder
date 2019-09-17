function W = generateW(T, D)
% generateW - compute the W matrix defined in Toda et al., 2007
%
% Syntax: W = generateW(T, D)
%
% Inputs:
% 	T - the length of a MFCC list
% 	D - the dimension of the MFCC
%
% Outputs:
% 	W - a 2DT * DT matrix.
%
% Other m-files required: None
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: Oct. 2015; Last revision: 05/18/2017
% Revision log:
% 	11/19/2015: updated function descriptions
% 	1/8/2016: updated function descriptions
%   05/18/2017: fixed a bug that causes the last static frame to be empty, GZ

%------------- BEGIN CODE --------------
% Adapted from https://github.com/r9y9/VoiceConversion.jl/blob/master/src/trajectory_gmmmap.jl
W = sparse([]);
t = 1;
w0 = zeros(D, D * T);
w1 = zeros(D, D * T);
w1(:, t * D + 1:(t + 1) * D) = 0.5 * eye(D);
w0(:, (t - 1) * D + 1:t * D) = eye(D);
W(2 * D * (t - 1) + 1:2 * D * t,:) = [w0; w1];
for t=2:T - 1
    w0 = zeros(D, D * T);
    w1 = zeros(D, D * T);
    w0(:, (t - 1) * D + 1:t * D) = eye(D);
    w1(:, (t - 2) * D + 1:(t - 1) * D) = -0.5 * eye(D);
    w1(:, t * D + 1:(t + 1) * D) = 0.5 * eye(D);   
    W(2 * D * (t - 1) + 1:2 * D * t,:) = [w0; w1];
end
t = T;
w0 = zeros(D, D * T);
w0(:, (t - 1) * D + 1:t * D) = eye(D);
w1 = zeros(D, D * T);
w1(:, (t - 2) * D + 1:(t - 1) * D) = -0.5 * eye(D);
W(2 * D * (t - 1) + 1:2 * D * t,:) = [w0; w1];
end