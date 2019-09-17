% Test voiceConversionGSB

function tests = voiceConversionGSBTest
    tests = functiontests(localfunctions);
end

function setupOnce(testCase)
    testUttPath = '/var/gzhao/test_data/src/cache/mat/gsb_0001.mat';
    testCase.TestData.utt = loadUttGSB({testUttPath},...
        'RegExp', '^(?!post)\w');
    
    gmmMdlPath = '/var/gzhao/test_data/model/acoustic/ppg_gmm_model.mat';
    testCase.TestData.gmmMdl = load(gmmMdlPath);
    
    srcPitchMdlPath = '/var/gzhao/test_data/model/pitch/src_model.mat';
    testCase.TestData.srcPitchMdl = load(srcPitchMdlPath);
    
    tgtPitchMdlPath = '/var/gzhao/test_data/model/pitch/tgt_model.mat';
    testCase.TestData.tgtPitchMdl = load(tgtPitchMdlPath);
end

function teardownOnce(testCase)
    testCase.TestData = [];
end

function testVoiceConversionGSBmlgv(testCase)
    [covUtt, status] = voiceConversionGSB(testCase.TestData.utt,...
        testCase.TestData.gmmMdl, testCase.TestData.srcPitchMdl,...
        testCase.TestData.tgtPitchMdl, 'SpecCov', 'MLGV');
    isValidWav = sum(isnan(covUtt.wav)) == 0;
    verifyTrue(testCase, isValidWav);
    verifyTrue(testCase, logical(status));
end

function testVoiceConversionGSBmlpg(testCase)
    [covUtt, status] = voiceConversionGSB(testCase.TestData.utt,...
        testCase.TestData.gmmMdl, testCase.TestData.srcPitchMdl,...
        testCase.TestData.tgtPitchMdl, 'SpecCov', 'MLPG');
    isValidWav = sum(isnan(covUtt.wav)) == 0;
    verifyTrue(testCase, isValidWav);
    verifyTrue(testCase, logical(status));
end

function testVoiceConversionGSBmmse(testCase)
    [covUtt, status] = voiceConversionGSB(testCase.TestData.utt,...
        testCase.TestData.gmmMdl, testCase.TestData.srcPitchMdl,...
        testCase.TestData.tgtPitchMdl, 'SpecCov', 'MMSE');
    isValidWav = sum(isnan(covUtt.wav)) == 0;
    verifyTrue(testCase, isValidWav);
    verifyTrue(testCase, logical(status));
end