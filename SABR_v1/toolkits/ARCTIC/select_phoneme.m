function [data] = select_phoneme(phoneme, processed_dir, files, fields)

if(nargin < 4)
    fields{1} = 'spectrum';
end

if(nargin < 3 || isempty(files))
    %only select "A" files if we have no file list
    files = dir([processed_dir '/*arctic_a*.mat']);
end

data = cell(1,length(fields));

for i=1:length(fields)
    disp([9 'Capturing field ' num2str(i)]);
    data{i} = select_field_by(processed_dir, files, ...
        @(x) strcmpi(x.phonemes,phoneme), fields{i});
end