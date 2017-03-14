function wts = weights(centroids, spectrum, sparse_penalty, basis)

if(nargin < 4)
   basis = 2:24;
end

warning('off', 'MATLAB:nearlySingularMatrix');  

A = centroids(basis,:);
b = spectrum(basis,:);

param.lambda=sparse_penalty;
param.pos = 1;
param.mode = 2;

%weights = mexLasso(b,A,param);
wts = zeros(size(centroids,2),size(spectrum,2));

wts = NNLSKernelBatch(A,b);
%for i=1:size(spectrum,2)
%    wts(:,i) = lasso(A,b(:,i),'lambda',sparse_penalty);
%end

%wts(wts < 0) = -wts(wts < 0);
%weights = pinv(A) * b;
end