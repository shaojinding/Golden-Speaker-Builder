function [p,lambda_0, best_err] = optimize_warp(src_mfcc, tgt_mfcc)

S = [0.4:0.1:1.6];
Lambda_0 = [0.4:0.025:0.8];

best_err = Inf;

n_mfcc = length(src_mfcc);

DCT = warp.linear_cep(n_mfcc,n_mfcc,1,1);

for s=S
    for l_0 = Lambda_0
        C_tilde = warp.linear_cep(n_mfcc,n_mfcc,s,l_0);
        warp_mfcc = DCT'*C_tilde*[0; src_mfcc(2:end)];
        err = sum((warp_mfcc - [0; tgt_mfcc(2:end)]).^2);
        
        if(err < best_err)
            best_err = err;
            p = s;
            lambda_0 = l_0;
        end
    end
end

end