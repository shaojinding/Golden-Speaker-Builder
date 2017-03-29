function y=testStraightFiles(dirIn)
%checks to see which files are corrupt and offers to delete them

if ~exist(dirIn,'dir')
    error(['Directory ' dirIn ' not found.']);
end
dirIn=fixDir(dirIn);

%having some problems with STRAIGHT mat files saved on network, try copying from network then load locally
s=which('saveStraight');
f=fileparts(s);
tempDir=fixDir([f '\temp\']);

allS=findFiles(dirIn,'*_straight_*.mat');

test=ones(size(allS));

for i=1:size(test,1)
    %try to load
    try
        system(['copy ' dirIn allS(i,:) ' ' tempDir allS(i,:)]);
        load([tempDir allS(i,:)])
        system(['del ' tempDir allS(i,:)]);%cleanup
        disp([allS(i,:) ' ...success'])
    catch
        disp([allS(i,:) ' ...corrupt'])
        test(i)=0;
    end
end

y=allS(~test,:);%return bad files, need to be deleted and recomputed

if ~isempty(y)
    reply=input('Would you like to delete the corrupt files? [y/n]','s');
    switch reply
        case {'y','Y'}
            for i=1:size(y,1)
                system(['del ' dirIn y(i,:)]);
            end
    end
end

end

function f=findFiles(dirIn,regExp)
%finds files in the specified directory satisfying the regular expression

f=ls([dirIn regExp]);

end