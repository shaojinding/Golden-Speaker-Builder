% Test voiceConversionInterfaceGSB

function tests = voiceConversionInterfaceGSBTest
    tests = functiontests(localfunctions);
end

function setup(testCase)
    testCase.TestData.gmmPath = '/var/gzhao/test_data/model/acoustic/ppg_gmm_model.mat';
    testCase.TestData.srcPitchPath = '/var/gzhao/test_data/model/pitch/src_model.mat';
    testCase.TestData.tgtPitchPath = '/var/gzhao/test_data/model/pitch/tgt_model.mat';
    testCase.TestData.outputPath = '/var/gzhao/test_data/temp/vc_test';
    
    if exist(testCase.TestData.outputPath, 'dir')
        rmdir(testCase.TestData.outputPath, 's');
    end
end

function teardown(testCase)
    if exist(testCase.TestData.outputPath, 'dir')
        rmdir(testCase.TestData.outputPath, 's');
    end
end

function testVoiceConversionInterfaceGSBoneUtt(testCase)
    testUtts = {'/var/gzhao/test_data/src/cache/mat/gsb_0001.mat'};
    outputFileName = fullfile(testCase.TestData.outputPath,...
        'gsb_0001.wav');
    
    [wavFiles, status] = voiceConversionInterfaceGSB(testUtts,...
        testCase.TestData.gmmPath, testCase.TestData.srcPitchPath,...
        testCase.TestData.tgtPitchPath, testCase.TestData.outputPath);
    
    % Wav is saved
    verifyTrue(testCase, logical(exist(wavFiles{1}, 'file')));
    % Wav is saved to the desired path
    verifyTrue(testCase, strcmp(wavFiles{1}, outputFileName));
    % Status is valid
    verifyTrue(testCase, logical(status));
end

function testVoiceConversionInterfaceGSBmultipleUttSerial(testCase)
    testUtts = {'/var/gzhao/test_data/src/cache/mat/gsb_0001.mat',...
        '/var/gzhao/test_data/src/cache/mat/gsb_0002.mat',...
        '/var/gzhao/test_data/src/cache/mat/gsb_0003.mat'};
    
    [wavFiles, status] = voiceConversionInterfaceGSB(testUtts,...
        testCase.TestData.gmmPath, testCase.TestData.srcPitchPath,...
        testCase.TestData.tgtPitchPath, testCase.TestData.outputPath,...
        'NumWorkers', 0);
    
    for ii = 1:length(wavFiles)
        % Wav is saved
        verifyTrue(testCase, logical(exist(wavFiles{ii}, 'file')));
    end
    % Status is valid
    verifyTrue(testCase, logical(status));
end

function testVoiceConversionInterfaceGSBmultipleUttParallel(testCase)
    testUtts = {'/var/gzhao/test_data/src/cache/mat/gsb_0001.mat',...
        '/var/gzhao/test_data/src/cache/mat/gsb_0002.mat',...
        '/var/gzhao/test_data/src/cache/mat/gsb_0003.mat'};
    
    [wavFiles, status] = voiceConversionInterfaceGSB(testUtts,...
        testCase.TestData.gmmPath, testCase.TestData.srcPitchPath,...
        testCase.TestData.tgtPitchPath, testCase.TestData.outputPath,...
        'NumWorkers', 4);
    
    for ii = 1:length(wavFiles)
        % Wav is saved
        verifyTrue(testCase, logical(exist(wavFiles{ii}, 'file')));
    end
    % Status is valid
    verifyTrue(testCase, logical(status));
end