/**
 * Created by dshj940428 on 10/19/2016.
 */
var cwd = null;
var goldenSpeakerName = null;
var wavesurferTeacher = null;
var wavesurfer = null;
var microphone = null;
var recorded = null;
var ifChoose = null;
var buildingGoldenSpeaker = null;
var uttrFiles = null;
var timeStamps = null;
$(document).ready( function() {
    if (ifChoose == "False") {
        wavesurferTeacher = WaveSurfer.create({
            container: '#wavesurf-teacher',
            waveColor: 'violet',
            progressColor: 'purple',
            height: '150',
        });
        // wavesurferTeacher.empty();
        // wavesurferTeacher.on('ready', function () {
        //     var spectrogram = Object.create(WaveSurfer.Spectrogram);
        //
        //     spectrogram.init({
        //         wavesurfer: wavesurferTeacher,
        //         container: "#teacher-spec"
        //     });
        //     var timeline = Object.create(WaveSurfer.Timeline);
        //     timeline.init({
        //         wavesurfer: wavesurferTeacher,
        //         container: '#teacher-timeline',
        //         //primaryFontColor: 'white',
        //     });
        // });

        wavesurfer = WaveSurfer.create({
            container: '#wavesurf-student',
            waveColor: 'violet',
            progressColor: 'purple',
            height: '150',
        });
        wavesurfer.empty();
        microphone = Object.create(WaveSurfer.Microphone);
        microphone.init({
            wavesurfer: wavesurfer
        });
        wavesurfer.on('ready', function () {
            // if (recorded) {
            //     var spectrogram = Object.create(WaveSurfer.Spectrogram);
            //     spectrogram.init({
            //         wavesurfer: wavesurfer,
            //         container: "#student-spec"
            //     });
            // }
            var timeline = Object.create(WaveSurfer.Timeline);
            timeline.init({
                wavesurfer: wavesurfer,
                container: '#student-timeline',
                //primaryFontColor: 'white',
            });
        });
    }
    else {
        var timeStampContainer = document.getElementsByClassName("time-stamp");
        for (var i = 0; i < timeStampContainer.length; i++) {
            if ($.isNumeric(timeStamps[i])) {
                var time = moment.unix(timeStamps[i]).format("MMM D YYYY h:mm:ss");
            }
            else {
                var time = timeStamps[i];
            }

            timeStampContainer[i].innerText = time;
        }
        setTimeout ( "checkBuildStatus()", 30000 );
    }
    $(".synthesized-uttr").click(function () {
        $(".synthesized-uttr").removeClass('active');
        $(this).addClass('active');
        var name = $(this).attr('id');
        var source = document.getElementById("utterance-source");
        wavesurferTeacher.empty();
        var audioBase64 = uttrFiles["{0}_{1}".replace("{0}", goldenSpeakerName).replace("{1}", name)];
        var audioBlob = b64toBlob(audioBase64);
        var audioUrl = window.URL.createObjectURL(audioBlob);
        wavesurferTeacher.load(audioUrl);
        var playbtn = document.getElementById("playPause-teacher");
        playbtn.disabled = false;
        var downloadbtn = document.getElementById("download-teacher");
        downloadbtn.removeAttribute("disabled");
        downloadbtn.href = audioUrl;
        downloadbtn.download = "{0}_{1}.wav".replace("{0}", goldenSpeakerName).replace("{1}", name);
    });
    $("#playPause-teacher").click(function () {
        wavesurferTeacher.playPause();
        $(this).toggleClass("playing");
    });
    //$(".play-gs").click(function () {
        // var name = $(this).parent().attr('id');
        // var audio = document.getElementById("utterance-play");
        // var source = document.getElementById("utterance-source");
        // wavesurferTeacher.empty();
        // var audioBase64 = uttrFiles["{0}_{1}".replace("{0}", goldenSpeakerName).replace("{1}", name)];
        // var audioBlob = b64toBlob(audioBase64);
        // var audioUrl = window.URL.createObjectURL(audioBlob);
        // wavesurferTeacher.load(audioUrl);
        //wavesurferTeacher.play();
        //source.src = audioUrl;
        //audio.load();
        //audio.play();
    //});
    $("#record").click(function (){
        toggleRecordingPractice(this);
    });
    $("#playPause").click(function (){
        wavesurfer.playPause();
        $(this).toggleClass("playing");
    });
});

function checkBuildStatus() {
    if (buildingGoldenSpeaker!=null) {
        for (var i = 0; i < buildingGoldenSpeaker.length; i++) {
            $.get('/speech/get_synthesize_status/', {slug: buildingGoldenSpeaker[i]}, function (data) {
                var arr = JSON.parse(data);
                var name = arr[0];
                var status = arr[1];
                if (status == "Finished") {
                    alert("Your Golden Speaker '{0}' is built!".replace("{0}", name));
                    window.location.href = '/speech/practice/index'
                }
            });
        }
        setTimeout("checkBuildStatus()", 30000);
    }

}

function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}