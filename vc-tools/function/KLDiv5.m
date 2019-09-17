% Compute pairwise KL divergence
% This is a really fast implementation
% x: d*m matrix, each column is a sample
% y: d*n matrix, each column is a sample
% dist: m*n matrix, dist(i, j) = KL(x(:, i), y(:, j))

function D = KLDiv5(x, y)
    logx = log(x+eps);
    logy = log(y+eps);
    
    % D = bsxfun(@plus,dot(x,logx,1),dot(y,logy,1)')-logy'*x-y'*logx;
    % D = D';
    D = bsxfun(@plus,dot(y,logy,1),dot(x,logx,1)')-x'*logy-logx'*y;
end