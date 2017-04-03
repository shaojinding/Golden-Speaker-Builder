function y=saveStraight(dirIn,dirOut,f0bounds,filesIn)
%performs STRAIGHT analysis on files containing _a0_ in dirIn
%saves output in separate .mat files in dirOut with same prefix and suffix
% e.g. rgo_a0_0001.mat -> rgo_straight_0001.mat (contains f0raw,ap,n3sgram)
% note: also checks to see which files already exist in dirOut so it doesn't redo analysis 
%  - this is convinient because the analysis is so slow (allows stopping & starting)
% optionally allows fileList to be passed directly in

%first check to make sure dirIn and dirOut exist
%reminder- might need to map S:\ to \\scratch.cse.tamu.edu\prism\dlfelps
if ~exist(dirIn,'dir')
    error(['Directory ' dirIn ' not found.']);
end
if ~exist(dirOut,'dir')
    error(['Directory ' dirOut ' not found.']);
end

if nargin<2
    dirOut=dirIn;
end
dirIn=fixDir(dirIn);
dirOut=fixDir(dirOut);

if nargin<3
%   f0bounds=[75 215];%optimized for rgo
    f0bounds=[62 142];%optimized for mab
end
if nargin<4
    %creates file list
    allWav=findFiles(dirIn,'*_a0_*.mat');
    allS=findFiles(dirOut,'*_straight_*.mat');
    [preWav,postWav]=parseFiles(allWav,'_a0_');
    [preS,postS]=parseFiles(allS,'_straight_');
    if isempty(postS)%first time running
        diff=postWav;
    else
        diff=setdiff(postWav,postS,'rows');%some straight files already analyzed
    end
    if isempty(diff)
        disp('No differences found. Check to see if all files already exist.')
        y=diff;
        return;
    end
    
    filesIn=[preWav(1:size(diff,1),:) repmat('_a0_',size(diff,1),1) diff];
end

%having some problems with STRAIGHT mat files saved on network, try saving locally then copying to network location
s=which('saveStraight');
f=fileparts(s);
tempDir=fixDir([f '\temp\']);

for i=1:size(filesIn,1)
    filesOut(i,:)=regexprep(filesIn(i,:),'_a0_','_straight_');
end

%now we can get down to business
%first create default paramter struct
f0.F0searchLowerBound=f0bounds(1);
f0.F0searchUpperBound=f0bounds(2);
y=filesOut;
disp(['The following files will be created:']);
disp(y)
disp(3)
pause(1)
disp(2)
pause(1)
disp(1)
pause(1)

for i=1:size(filesIn,1)
    [x,fs]=readData(dirIn,filesIn(i,:));
    [f0raw,ap,n3sgram]=analyzeStraight(x,fs,f0);
    %save data to (local) tempDir first
    save([tempDir filesOut(i,:)],'f0raw','ap','n3sgram');
    %then copy to network location
    system(['copy ' tempDir filesOut(i,:) ' ' dirOut filesOut(i,:)]);
    %cleanup local directory
    system(['del ' tempDir filesOut(i,:)]);
    disp(filesOut(i,:))
end

end

function [f0raw,ap,n3sgram]=analyzeStraight(x,fs,f0)
%performs straight analysis
f0raw   = MulticueF0v14(x,fs,f0.F0searchLowerBound,f0.F0searchUpperBound);
[ap]      = exstraightAPind(x,fs,f0raw,f0);
[n3sgram] = exstraightspec(x,f0raw,fs);
end

function [x,fs]=readData(path,fileName)
%loads *.mat file containing audio and returns audio and fs

load([path fileName],'data','samplerate');
fs=16000;
x=resample(data,fs,samplerate);
            
end

function f=findFiles(dirIn,regExp)
%finds files in the specified directory satisfying the regular expression

f=ls([dirIn regExp]);

end

function [pre,post]=parseFiles(fileList,midStr)
%returns pre and post forms of strings separated by midStr
%assumes all fileNames are same length

if isempty(fileList)
    pre=[];
    post=[];
    return;
end

if ~isstr(fileList)
    fileList=char(fileList);
end

%should not contain spaces if all strings in list are same length
testSpaces=fileList(:);
if any(isspace(testSpaces))
    error('Filenames do not all have the same length')
end

%find location of midStr within first string
start=findstr(fileList(1,:),midStr);
preLoc=start-1;
postLoc=start+length(midStr);
pre=fileList(:,1:preLoc);
post=fileList(:,postLoc:end);
end



