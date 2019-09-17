% Test buildPitchModelGSB

function tests = buildPitchModelGSBTest
    tests = functiontests(localfunctions);
end

function setup(testCase)
    mats = dir('/var/gzhao/test_data/src/cache/mat/*.mat');
    numMats = length(mats);
    matList = cell(numMats, 1);
    for ii = 1:numMats
        matList{ii} = fullfile('/var/gzhao/test_data/src/cache/mat',...
            mats(ii).name);
    end
    
    testCase.TestData.mats = matList;
    testCase.TestData.outputPath = '/var/gzhao/test_data/temp/build_pitch_test/model.mat';
    
    testCase.TestData.outputDir = fileparts(testCase.TestData.outputPath);
    if exist(testCase.TestData.outputDir, 'dir')
        rmdir(testCase.TestData.outputDir, 's');
    end
end

function teardown(testCase)
    if exist(testCase.TestData.outputDir, 'dir')
        rmdir(testCase.TestData.outputDir, 's');
    end
end

function testBuildPitchModelGSBheq(testCase)
    [modelPath, status] = buildPitchModelGSB(testCase.TestData.mats,...
        testCase.TestData.outputPath, 'Mode', 'heq');
    verifyTrue(testCase, logical(status));
    verifyTrue(testCase, logical(exist(modelPath, 'file')));
end

function testBuildPitchModelGSBlog(testCase)
    [modelPath, status] = buildPitchModelGSB(testCase.TestData.mats,...
        testCase.TestData.outputPath, 'Mode', 'log');
    verifyTrue(testCase, logical(status));
    verifyTrue(testCase, logical(exist(modelPath, 'file')));
end