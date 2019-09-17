% Test data prep
% - Serial mode: run on one core
% - Parallel mode: run on multiple cores

function tests = dataPrepTest
    tests = functiontests(localfunctions);
end

function setup(testCase)
    % Prepare the testing audio files
    rootDir = '/var/gzhao/test_data/src/recordings';
    recordings = dir(fullfile(rootDir, '*.wav'));
    numWavs = length(recordings);
    wavList = cell(numWavs, 1);
    endTime = zeros(numWavs, 1);
    for ii = 1:numWavs
        wavList{ii} = fullfile(rootDir, recordings(ii).name);
        [wav, fs] = audioread(wavList{ii});
        audioLength = length(wav)/fs;
        endTime(ii) = audioLength - 0.01;
    end
    testCase.TestData.numWavs = numWavs;
    testCase.TestData.wavList = wavList;
    testCase.TestData.transFile = '/var/gzhao/test_data/src/prompts.txt';
    testCase.TestData.outputDir = '/var/gzhao/test_data/temp/dataprep_test';
    testCase.TestData.startTime = 0.01 * ones(numWavs, 1);
    testCase.TestData.endTime = endTime;
    
    % Prepare temp output dir
    if exist(testCase.TestData.outputDir, 'dir')
        rmdir(testCase.TestData.outputDir, 's');
    end
end

function teardown(testCase)
    if exist(testCase.TestData.outputDir, 'dir')
        rmdir(testCase.TestData.outputDir, 's');
    end
end

function testDataPrepSerial(testCase)
    matList = dataPrep(testCase.TestData.wavList,...
        testCase.TestData.transFile, testCase.TestData.outputDir,...
        'NumWorkers', 0, 'StartTime', testCase.TestData.startTime,...
        'EndTime', testCase.TestData.endTime);
    verifyEqual(testCase, length(matList), testCase.TestData.numWavs);
    % All files exist
    for ii = 1:testCase.TestData.numWavs
        verifyTrue(testCase, logical(exist(matList{ii}, 'file')));
    end
end

function testDataPrepParallel(testCase)
    matList = dataPrep(testCase.TestData.wavList,...
        testCase.TestData.transFile, testCase.TestData.outputDir,...
        'NumWorkers', 8, 'StartTime', testCase.TestData.startTime,...
        'EndTime', testCase.TestData.endTime);
    verifyEqual(testCase, length(matList), testCase.TestData.numWavs);
    % All files exist
    for ii = 1:testCase.TestData.numWavs
        verifyTrue(testCase, logical(exist(matList{ii}, 'file')));
    end
end