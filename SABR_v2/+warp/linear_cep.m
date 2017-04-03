function C_tilde = linear_cep(M,N,p,lambda_0)

%M is the number of Mel-scaled filterbanks
%N is the number of cepstral coefficients

C_tilde = zeros(M,N);

warp_fun = @(x) theta(p,x,lambda_0);

for m=1:M
    for k=1:N
        a_k = alpha_k(k-1,M);
        C_tilde(m,k) = a_k * cos(pi*(k-1)*warp_fun((2*m-1)/(2*M)));
    end
end

end

function alpha = alpha_k(k,M)
if(k == 0)
    alpha = sqrt(1/M);
else
    alpha = sqrt(2/M);
end
end

function v = theta(p,lambda, lambda_0)
    if(lambda <= lambda_0)
        v = p*lambda;
    else
        v = p*lambda_0;
        v = v + (1 - (p*lambda_0))/(1-lambda_0)*(lambda-lambda_0);
    end
end