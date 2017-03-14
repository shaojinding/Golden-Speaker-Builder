function preprocess_speaker( indir, outputdir, spec_method, utts, skipspec)
%PREPROCESS_SPEAKER preprocess an ARCTIC speaker
%   Preprocesses the utterances in inputdir and places them in outputdir
%   Parameters
%      - indir: ARCTIC speaker root directory
%      - outputdir: where each utterance's preprocessed structure is put
%      - spec_method: a function which maps the audio to a spectral
%          representation at the sampling rate specified by sr.
%          Form: (X,SR) -> SPEC
%      - files: a list of files in inputdir to actually consider

if(nargin < 5)
    skipspec = 0;
end

[utts] = checkargin(indir, outputdir, spec_method, utts);

wavpath = [indir '/wav/'];
phpath  = [indir '/lab/'];

for i=1:length(utts)
    utt_name = [utts{i}];
    
    fprintf('Processing %s\n',  utt_name);
    
    if(skipspec)
        load([outputdir '/' utt_name '.mat']);
        f0    = u.f0;
        spec  = u.spectrum;
        ap    = u.ap;
        audio = u.audio;
        sr    = u.sr;
    else
        %open audio
        [audio,sr]  = audioread([wavpath utt_name '.wav']);

        %extract MFCCs based on config file
        [f0,spec,ap] = spec_method(audio,sr);
    end
    
    %extract phonememes
    %open the utterance phonemic transcription and audio
    ph_fid = fopen([phpath utt_name '.lab']);
    %advance phoneme file after initial blank comment line
    fgets(ph_fid);
    ph   = preprocess_phones(ph_fid,0.001, size(spec,2));
    fclose(ph_fid);
    
    u.phonemes    = ph;
    u.spectrum    = spec;
    u.f0          = f0;
    u.ap          = ap;
    u.spec_method = spec_method;
    u.audio       = audio;
    u.sr          = sr;
    
    save([outputdir '/' utt_name '.mat'],'u');
end

end

function utts = checkargin(indir, outputdir, spec_method, utts)

    if(~exist(indir,'dir'))
       error(['Unable to find input speaker directory ' indir]); 
    end
    
    utt_file = [indir '/etc/txt.done.data'];
    
    if(~exist(utt_file,'file'))
        error('cannot find utterance file');
    end
    
    if(~exist(outputdir,'dir'))
        success = mkdir(outputdir);
        if(~success)
            error(['Unable to make output directory ' outputdir]);
        end
    end
    
    if(~isa(spec_method,'function_handle'))
        error(['SPEC_METHOD needs to be a function handle']);
    end
    
    if(isempty(utts))
        %get all utterances
        fid = fopen([indir '/etc/txt.done.data']);
        t_s = textscan(fid,'( %s %q )');
        fclose(fid);

        utts = strtrim(t_s{1});
    end
end

function [ P ] = preprocess_phones( phoneme_fid, win_inc, mfcc_samples )
%PHONES Summary of this function goes here
%   Detailed explanation goes here

%using the information from the MFCCs, we extract the phoneme-level
%information at the same intervals as the MFCCs which allow us to label the
%phones accordingly.
config_mfcc;

P = cell(mfcc_samples,1);

p_info = textscan(phoneme_fid,'%f %f %s');

if(p_info{1}(2) > 1e3) %if we have nanoseconds, not seconds
    p_info{1} = p_info{1}./1e7;
    p_info{2} = p_info{2}./1e7;
end

%convert 'sil' to 'pau
p_info{3}(cellfun(@(x) strcmpi(x,'sil'),p_info{3})) = {'pau'};

p_times = [p_info{1}];

%step through each of the P indicies; when we get to an index that's
%advanced to the next phoneme based on info in p_info, we update the value
%in P. recall each index in P maps to an idnex in the MFCC feature vector,
%and each index also maps to a specific start time
for i=1:length(P)
 t_idx = (i-1)*(win_inc);
 %ph_idx = find(p_times < t_idx,1,'last'); %change for RGO?
 ph_idx = find(p_times >= t_idx,1,'first');

 %just choose the last phoneme if for wahtever reason the index we're
 %asking for is out of bounds
 if(isempty(ph_idx))
   ph_idx = length(p_info{3});
 end

 P{i} = p_info{3}{ph_idx};
end

end
