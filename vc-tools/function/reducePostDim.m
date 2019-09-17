% reduce post dim from 5816 to 40, assume it already has post
function post40 = reducePostDim (post)
load('D:\\GDriveTAMU\\PSI Lab\\corpora\\helpers\\function\\reduce_dim.mat', 'phonesCleanedUp');

plabs = {'aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'b', 'ch', 'd', 'dh', ...
        'eh', 'er', 'ey', 'f', 'g', 'hh', 'ih', 'iy', 'jh', 'k', 'l', 'm', ...
        'n', 'ng', 'ow', 'oy', 'p', 'r', 's', 'sh', 't', 'th', 'uh', 'uw', ...
        'v', 'w', 'y', 'z', 'zh', 'sil'};
numPhonemes = length(plabs);

% Reduce dims
post40 = zeros(numPhonemes, size(post, 2)); % ouput
for ii = 1:numPhonemes
    post40(ii, :) = sum(post(phonesCleanedUp(plabs{ii}), :));
end
