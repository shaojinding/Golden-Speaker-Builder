% Test buildGMMmodelGSB

function tests = buildGMMmodelGSBTest
    tests = functiontests(localfunctions);
end

function setup(testCase)
    srcMats = dir('/var/gzhao/test_data/src/cache/mat/*.mat');
    numMats = length(srcMats);
    srcMatList = cell(numMats, 1);
    for ii = 1:numMats
        srcMatList{ii} = fullfile('/var/gzhao/test_data/src/cache/mat',...
            srcMats(ii).name);
    end
    
    tgtMats = dir('/var/gzhao/test_data/tgt/cache/mat/*.mat');
    numMats = length(tgtMats);
    tgtMatList = cell(numMats, 1);
    for ii = 1:numMats
        tgtMatList{ii} = fullfile('/var/gzhao/test_data/tgt/cache/mat',...
            tgtMats(ii).name);
    end
    
    testCase.TestData.srcMats = srcMatList;
    testCase.TestData.tgtMats = tgtMatList;
    testCase.TestData.outputPath = '/var/gzhao/test_data/temp/build_gmm_test/model.mat';
    
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

function testBuildGMMmodelGSBnormal(testCase)
    [modelPath, status] = buildGMMmodelGSB(testCase.TestData.srcMats,...
        testCase.TestData.tgtMats, testCase.TestData.outputPath);
    verifyTrue(testCase, logical(status));
    verifyTrue(testCase, logical(exist(modelPath, 'file')));
end