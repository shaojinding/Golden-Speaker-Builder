function [ new_f0 ] = adj_f0( src_f0, tgt_f0_mean, tgt_f0_std )

log_f0 = log(src_f0);
std_f0 = std(log_f0(src_f0 > 0));
new_f0 = (log_f0 - mean(log_f0(src_f0 > 0))) * (tgt_f0_std/std_f0) + tgt_f0_mean; 
new_f0 = exp(new_f0);
new_f0(src_f0 == 0) = 0;

end

