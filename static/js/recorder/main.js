/**
 * Created by dshj940428 on 10/12/2016.
 */
var audio_context;
var recorder;
var record_url = null;
var record_blob = null;
function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    recorder = new Recorder(input);
}

function startRecording() {
    recorder && recorder.record();
}

function stopRecording() {
    recorder && recorder.stop();
    createDownloadLink();
    recorder.clear();
}

function toggleRecording( e ) {
    if (e.classList.contains("recording")) {
        // stop recording
        stopRecording();
        microphone.stop();
        wavesurfer.enableDragSelection({
            color: 'hsla(400, 100%, 30%, 0.1)',
            drag: false
        });
        regionEnabled = true;
        e.classList.remove("recording");
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = false;
        isRecording = false;
    } else {
        // start recording
        if (!recorder)
            return;
        e.classList.add("recording");
        if ($.inArray(currentPhoneme, savedPhoneme) >=0) {
            reRecord = true;
        }
        var zoominbtn = document.getElementById("zoomin");
        zoominbtn.disabled = true;
        var zoomoutbtn = document.getElementById("zoomout");
        zoomoutbtn.disabled = true;
        var savebtn = document.getElementById("save");
        savebtn.disabled = true;
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = true;
        isRecording = true;
        microphone.start();
        if (regionEnabled) {
            wavesurfer.empty();
            wavesurfer.clearRegions();
            wavesurfer.disableDragSelection();
            regionEnabled = false;
        }

        startRecording();
    }
}

function toggleRecordingPitch( e ) {
    if (e.classList.contains("recording")) {
        // stop recording
        stopRecording();
        microphone.stop();
        e.classList.remove("recording");
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = false;
        var savebtn = document.getElementById("save");
        savebtn.disabled = false;
    } else {
        // start recording
        if (!recorder)
            return;
        e.classList.add("recording");
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = true;
        microphone.start();
        startRecording();
    }
}

function toggleRecordingPractice( e ) {
    if (e.classList.contains("recording")) {
        // stop recording
        stopRecording();
        microphone.stop();
        wavesurfer.enableDragSelection({
            color: 'hsla(400, 100%, 30%, 0.1)',
            drag: false
        });
        recorded = true;
        e.classList.remove("recording");
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = false;
    } else {
        // start recording
        if (!recorder)
            return;
        e.classList.add("recording");
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = true;
        var downloadbtn = document.getElementById("download");
        downloadbtn.disabled = true;
        recorded = false;
        microphone.start();
        startRecording();
    }
}

function createDownloadLink() {
    recorder && recorder.exportWAV(wavesurfGetBlob);
}

function wavesurfGetBlob(blob) {
    wavesurfer.loadBlob(blob);
    record_blob = blob;
    record_url = URL.createObjectURL(blob);
    record_url = record_url.substring(5, record_url.length);
}

window.onload = function init() {
    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;
    } catch (e) {
        alert('No web audio support in this browser!');
    }

    navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
        alert('No web audio support in this browser!');
    });
};