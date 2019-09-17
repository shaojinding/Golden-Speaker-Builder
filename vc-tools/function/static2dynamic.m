function X = static2dynamic(x)
%% static2dynamic - Transform the static MFCCs x to the dynamic version X = (x, dx);
%					The result of this function is the same as X = Wx, but it's faster and requires less memory.
%
% Syntax: X = static2dynamic(x)
%
% Inputs:
% 	x - a [D, T] MFCC matrix
%
% Outputs:
% 	X - a [2D, T] (MFCC + Delta MFCC) matrix
%
% Other m-files required: None
%
% Subfunctions: None
%
% MAT-file required: None
%
% Author: Guanlong Zhao
% Email: gzhao@tamu.edu
% Created: Oct. 2015; Last revision: 04/27/2017
% Revision log:
% 	11/19/2015: updated the function descriptions
%	1/8/2016: updated the function descriptions
%   04/27/2017: compatibility fix, GZ

%------------- BEGIN CODE --------------
x = transpose(x); % D*T -> T*D

[T, D] = size(x);
X = zeros(T, 2 * D);
x1_dx1 = [x(1, :), x(2, :) .* 0.5];
X(1, :) = x1_dx1;
for t = 2:T - 1
    xt_dxt = [x(t, :), (x(t + 1, :) - x(t - 1, :)) .* 0.5];
    X(t, :) = xt_dxt;
end
xT_dxT = [x(T, :), x(T - 1, :) .* (-0.5)];
X(T, :) = xT_dxT; % T * 2D

X = transpose(X); % T*2D -> 2D*T
end