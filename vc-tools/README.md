# Accent Conversion Tools for Golden Speaker Builder (GSB)
This branch implements the accent conversion algorithm described in the following paper as a backend system for [Golden Speaker Builder](http://goldenspeaker.las.iastate.edu/speech/). Each function has a detailed documentation.

```
@inproceedings{zhao2018accent,
  author={G. Zhao and S. Sonsaat and J. Levis and E. Chukharev-Hudilainen and R. Gutierrez-Osuna}, 
  booktitle={Proc. ICASSP}, 
  title={Accent Conversion Using Phonetic Posteriorgrams}, 
  year={2018}, 
  pages={5314-5318}, 
  doi={10.1109/ICASSP.2018.8462258}, 
  ISSN={2379-190X}, 
  month={April}
}
```

## Functions
- `buildGMMmodelGSB`: Build a joint-density GMM model for accent conversion using the PPG-pairing
- `buildPitchModelGSB`: Build a pitch model
- `dataPrep`: Batch processing function that generates everything we need
- `loadUttGSB`: A very easy to use function that loads in pre-cached utterance structs
- `speechAnalysis`: Convert a wave file to an easy-to-process utterance struct
- `speechSynthesis`: Resynthesize speech from an utterance struct
- `voiceConversionGSB`: Convert a given source utterance, require a joint spectral model and pitch models from source and target speakers
- `voiceConversionInterfaceGSB`: An interface that exposes `voiceConversionGSB` and supports batch processing
- Other functions: `calculateGlobalVar`, `exFeaturesAPI`, `fixPpgLengthMismatch`, `framePairingPPG`, `generateW`, `getDerivatives`, `KLDiv5`, `phones2numeric`, `pitchConversion`, `prepareDataGMM`, `tg2lab`, `tryCreateDir`, `trySaveStructFields` 

## Scripts
- `prepareFixturesForTests`: Generate fixtures for tests
- `addDependencies`: Add all necessary dependencies to Matlab path

## Tests
- `test` contains all the tests for this package
- To run all tests, go to the `test` folder in Matlab, and type `runtests`; all tests take about 30 min to finish
- To run a particular test, type `runtests('TEST_NAME')`
- `ppgGmmEndToEndTest`: The end-to-end system test, can also be used as a reference on how the system works; this one takes about 10 min to finish

## Other dependencies
- [SpeechToolkitPSI](https://github.tamu.edu/guanlong-zhao/SpeechToolkitPSI/tree/gsb): gsb branch
  - acoust_based/*
  - GMM/*
  - kaldi2matlab/*
  - netlab/*
  - mcep-sptk-matlab/*
  - mPraat/*
  - Montreal-Forced-Aligner-1.0.0/dist/montreal-forced-aligner/*
  - rastamat/*
  - STRAIGHTV40_007c/*
  - TandemSTRAIGHTmonolithicPackage012/*
  - world-0.2.3_matlab/*
- [kaldi-posteriorgram](https://github.tamu.edu/guanlong-zhao/kaldi-posteriorgram/tree/gsb): gsb branch
- [f0_heq](https://github.tamu.edu/guanlong-zhao/f0_heq/tree/gsb): gsb branch
- [kaldi-5.3](https://github.com/kaldi-asr/kaldi/tree/5.3)

## Notes
- For functional details, please refer to each individual file's documentation
- Please kindly report any bug you find

Guanlong Zhao (gzhao@tamu.edu)

PSI lab

Department of Computer Science and Engineering, Texas A&M University

###### Last edit: Wed Oct 24 22:19:46 CDT 2018