function [ success ] = build_sabr_model( anchor_wav_list, left_list, right_list, anchor_labels, pitch_file, output_mat_file )

%verify each anchor file
config;
for i=1:length(anchor_wav_list)
    if(~exist(anchor_wav_list{i}))
        error(['FILE NOT FOUND: ' anchor_wav_list{i} ' does not exist!.']);
    end
end

if(length(left_list) ~= length(right_list))
    error(['LEFT AND RIGHT boundary vectors are different sizes']);
end

if(length(anchor_labels) ~= length(anchor_wav_list))
    error(['ANCHOR LABELS ARE DIFFERENT LENGTH THAN ANCHOR WAVE FILE LIST']);
end

if(length(anchor_labels) ~= length(left_list))
    error('ANCHOR FILE LIST IS DIFFERENT LENGTH THAN BOUNDARY LISTS');
end

[p,f,e] = fileparts(output_mat_file);

if(~exist(p))
    error(['OUTPUT PATH ' p ' DOES NOT EXIST']);
end

sabr_model = struct('anchors',[],'labels',[],'f0_mean',0,'f0_std',0);
sabr_model.labels = anchor_labels;

mfcc_comp  = @(x,sr) spectrum.spec2mfcc(x,sr,25,0);

%% Extract each anchor 

for i=1:length(anchor_wav_list)
    
    [audio,sr] = audioread(anchor_wav_list{i});
    
    %if the audio sampling rate does not have the required 16khz
    if(sr ~= 16e3)
        audio = resample(audio(:,1),16e3,sr);
        sr = 16e3;
    end
    
    audio = audio + 0.001*rand(size(audio));
    
    left_frame  = floor(left_list(i) * sr)+1;
    right_frame = floor(right_list(i) * sr);
    
    frame_length = 80;
    
    disp(['Processing phoneme /' anchor_labels(i) '/']);
    
    try
        disp('Extracting F0');
        f0 = MulticueF0v14  (audio(left_frame:right_frame),sr);
        disp('Extracting spectrum');
        spec = exstraightspec(audio(left_frame:right_frame),f0, sr);
    catch
        disp([ 9 'F0 extraction failed! Making zero vector for F0']);
        fake_pitch = zeros(1,ceil((right_frame-left_frame)/frame_length));
        disp('Extracting spectrum');
        spec = exstraightspec(audio(left_frame:right_frame),fake_pitch, sr);
    end
    
    comp_spec = mfcc_comp(spec,sr);
    
    sabr_model.anchors(:,i) = mean(comp_spec,2);    
end

%% Extract pitch

[pitch_audio, sr] = audioread(pitch_file);

%if the audio sampling rate does not have the required 16khz
if(sr ~= 16e3)
    pitch_audio = resample(pitch_audio(:,1),16e3,sr);
    sr = 16e3;
end

prmF0.F0defaultWindowLength = 80;
prmF0.F0frameUpdateInterval = 1; %in milliseconds
prmF0.F0searchLowerBound    = 50;
prmF0.F0SearchUpperBound    = 400;

Q.tframe=0.001;

tic;
f0 = MulticueF0v14  (pitch_audio(1:end),sr, prmF0);

%f0 = fxrapt(pitch_audio(1:end), sr, 'u', Q);
%f0(isnan(f0)) = 0;

toc;

sabr_model.f0_mean = mean(log(f0(f0 > 0)));
sabr_model.f0_std  = std (log(f0(f0 > 0)));

save(output_mat_file,'sabr_model');

if(exist(output_mat_file))
    success = 1;
else
    success = 0;
end

end