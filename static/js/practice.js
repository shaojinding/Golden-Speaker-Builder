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
$(document).ready( function() {
    if (ifChoose == "False") {
        wavesurferTeacher = WaveSurfer.create({
            container: '#wavesurf-teacher',
            waveColor: 'violet',
            progressColor: 'purple',
            height: '0',
        });
        wavesurferTeacher.empty();
        wavesurferTeacher.on('ready', function () {
            var spectrogram = Object.create(WaveSurfer.Spectrogram);

            spectrogram.init({
                wavesurfer: wavesurferTeacher,
                container: "#teacher-spec"
            });
            var timeline = Object.create(WaveSurfer.Timeline);
            timeline.init({
                wavesurfer: wavesurferTeacher,
                container: '#teacher-timeline',
                //primaryFontColor: 'white',
            });
        });

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
            if (recorded) {
                var spectrogram = Object.create(WaveSurfer.Spectrogram);
                spectrogram.init({
                    wavesurfer: wavesurfer,
                    container: "#student-spec"
                });
            }
            var timeline = Object.create(WaveSurfer.Timeline);
            timeline.init({
                wavesurfer: wavesurfer,
                container: '#student-timeline',
                //primaryFontColor: 'white',
            });
        });
    }
    $(".synthesized-uttr").click(function () {
        $(".synthesized-uttr").removeClass('active');
        $(this).addClass('active');
        // var name = $(this).attr('id');
        // var audio = document.getElementById("utterance-play");
        // var source = document.getElementById("utterance-source");
        // source.src = "/static/output_wav/" + goldenSpeakerName + '/' + name + '.wav';
        // audio.load();
    });
    $(".play-gs").click(function () {
        var name = $(this).parent().attr('id');
        var audio = document.getElementById("utterance-play");
        var source = document.getElementById("utterance-source");
        wavesurferTeacher.empty();
        wavesurferTeacher.load("/static/output_wav/" + goldenSpeakerName + '/' + name + '.wav');
        source.src = "/static/output_wav/" + goldenSpeakerName + '/' + name + '.wav';
        audio.load();
        audio.play();
    });
    $("#record").click(function (){
        toggleRecordingPractice(this);
    });
    $("#playPause").click(function (){
        wavesurfer.playPause();
        $(this).toggleClass("playing");
    });
});

