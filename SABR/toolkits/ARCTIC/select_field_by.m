function [data] = select_field_by(processed_dir, files, selection_criteria, field)

if(nargin < 4)
    field = 'spectrum';
end

if(nargin < 3 || isempty(files))
    %only select "A" files if we have no file list
    files = dir([processed_dir '/*arctic_a*.mat']);
end

frame_count = 0;

%for each utterance, count how many of the phoneme instances there are
for j=1:length(files)
    filename = files(j).name;
    load([processed_dir '/' filename], '-mat'); %force mat file loading
    
    disp(['Counting instances of in ' filename]);
    %count each phoneme
    frame_count = frame_count + sum(selection_criteria(u));
end

data = [];

%For each field
   
total_samples = 0;

for j=1:length(files)
    filename = files(j).name;
    load([processed_dir '/' filename], '-mat'); %force mat file loading

    disp(filename);

    idx = logical(selection_criteria(u));
    if(~any(idx))
       continue; 
    end
    
    if(eval(sprintf('isvector(u.%s)',field)))
        data(total_samples+1:total_samples+sum(idx)) = ...
            eval(sprintf('u.%s(idx);',field));
    else
        data(:,total_samples+1:total_samples+sum(idx)) = ...
            eval(sprintf('u.%s(:,idx);',field));
    end
    
    total_samples = total_samples+sum(idx);
end 
end