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
var regionVar = null;
var regionVarTeacher = null;
var regionEnabled = false;
var regionPlay = "teacher";
var ifTeacherLoad = false;
var zoomLevelTeacher = null;
var zoomMultiTeacher = 2;
var zoomLevelStudent = null;
var zoomMultiStudent = 2;
var centerTeacher = 0;
var centerStudent = 0;
var wavesurferWidth = null;
var microphone = null;
var slider = null;
var disp = null;
var playbackRate = 1.0;
var playbackRateRecord = 1.0;
var st = null;
var filter = null;
var node = null;
var audioUrl = null;
$(document).ready( function() {
    if (ifChoose == "False") {
        wavesurferTeacher = Object.create(WaveSurfer);
        wavesurferTeacher.init({
            container: '#wavesurf-teacher',
            waveColor: 'violet',
            progressColor: 'purple',
            height: '150',
            autoCenter: false,
            hideScrollbar: true,
        });
        wavesurferWidth = document.getElementById("wavesurf-teacher").offsetWidth;
        $("#panel-student").click(function () {
            regionPlay = "student";
        });
        $("#panel-teacher").click(function () {
            regionPlay = "teacher";
        });
        $("#zoomin-teacher").click(function () {
            var sec = wavesurferTeacher.getDuration();
            wavesurferTeacher.seekTo(centerTeacher / sec);
            wavesurferTeacher.zoom(zoomMultiTeacher * zoomLevelTeacher);
            zoomMultiTeacher = zoomMultiTeacher * 2;
            if (zoomMultiTeacher * zoomLevelTeacher >= 6400) {
                var zoominbtn = document.getElementById("zoomin-teacher");
                zoominbtn.disabled = true;
            }
            var zoomoutbtn = document.getElementById("zoomout-teacher");
            zoomoutbtn.disabled = false;
        });
        $("#zoomout-teacher").click(function () {
            var sec = wavesurferTeacher.getDuration();
            wavesurferTeacher.seekTo(centerTeacher / sec);
            wavesurferTeacher.zoom(zoomLevelTeacher);
            wavesurferTeacher.zoom(zoomLevelTeacher);
            zoomMultiTeacher = 2;
            var zoominbtn = document.getElementById("zoomin-teacher");
            zoominbtn.disabled = false;
            var zoomoutbtn = document.getElementById("zoomout-teacher");
            zoomoutbtn.disabled = true;

        });
        $("#zoomin-student").click(function () {
            var sec = wavesurfer.getDuration();
            wavesurfer.seekTo(centerStudent / sec);
            wavesurfer.zoom(zoomMultiStudent * zoomLevelStudent);
            zoomMultiStudent = zoomMultiStudent * 2;
            if (zoomMultiStudent * zoomLevelStudent >= 6400) {
                var zoominbtn = document.getElementById("zoomin-student");
                zoominbtn.disabled = true;
            }
            var zoomoutbtn = document.getElementById("zoomout-student");
            zoomoutbtn.disabled = false;
        });
        $("#zoomout-student").click(function () {
            var sec = wavesurfer.getDuration();
            wavesurfer.seekTo(centerStudent / sec);
            wavesurfer.zoom(zoomLevelStudent);
            wavesurfer.zoom(zoomLevelStudent);
            zoomMultiStudent = 2;
            var zoominbtn = document.getElementById("zoomin-student");
            zoominbtn.disabled = false;
            var zoomoutbtn = document.getElementById("zoomout-student");
            zoomoutbtn.disabled = true;
        });


        // tempo-scale-slider
        slider = document.getElementById("realtime-tempo-scale-slider");
        disp = document.getElementById("realtime-tempo-scale-disp");
        disp.innerHTML = "{0}%".replace("{0}", slider.value);
        slider.oninput = function() {
            disp.innerHTML = "{0}%".replace("{0}", this.value);
            playbackRate = 1.0 + slider.value / 100;
            playbackRateRecord = playbackRate;
            wavesurferTeacher.setPlaybackRate(playbackRate);
            // st.tempo = playbackRate;
        };
        wavesurferTeacher.on('ready', function () {
            ifTeacherLoad = true;
            wavesurferTeacher.enableDragSelection({
                color: 'hsla(400, 100%, 30%, 0.1)',
                drag: false,
                //resize: false,
            });
            var audioDuration = wavesurferTeacher.getDuration();
            zoomLevelTeacher = wavesurferWidth / audioDuration;
            wavesurferTeacher.on('region-update-end', function (region) {
                regionVarTeacher = region;
                regionPlay = "teacher";
                var start = region.start;
                var end = region.end;
                centerTeacher = (start + end) / 2;
                if (zoomMultiTeacher * zoomLevelTeacher < 6400) {
                    var zoominbtn = document.getElementById("zoomin-teacher");
                    zoominbtn.disabled = false;
                }
                if (zoomMultiTeacher != 2) {
                    var zoomoutbtn = document.getElementById("zoomout-teacher");
                    zoomoutbtn.disabled = false;
                }
                slider.value = 0.0;
                playbackRate = 1.0;
                disp.innerHTML = "disabled when segment selection";
                wavesurferTeacher.setPlaybackRate(playbackRate);
                slider.disabled = true;
            });
            wavesurferTeacher.on('region-removed', function () {
                regionVarTeacher = null;
                centerTeacher = 0;
                var zoominbtn = document.getElementById("zoomin-teacher");
                zoominbtn.disabled = true;
                if (zoomMultiTeacher <= 2) {
                    var zoomoutbtn = document.getElementById("zoomout-teacher");
                    zoomoutbtn.disabled = true;
                }
                wavesurferTeacher.clearRegions();
                wavesurferTeacher.disableDragSelection();
                wavesurferTeacher.backend.disconnectFilters();
                wavesurferTeacher.empty();
                wavesurferTeacher.load(audioUrl);
                playbackRate = playbackRateRecord;
                slider.value = (playbackRate - 1.0) * 100;
                disp.innerHTML = "{0}%".replace("{0}", slider.value);
                wavesurferTeacher.setPlaybackRate(playbackRate);
                slider.disabled = false;
            });
            //var playbackRate = 1.0 + slider.value / 100;
            //wavesurferTeacher.setPlaybackRate(playbackRate);
            // wavesurfer.backend.source.loop = false;
            st = new soundtouch.SoundTouch(wavesurferTeacher.backend.ac.sampleRate);
            var buffer = wavesurferTeacher.backend.buffer;
            var channels = buffer.numberOfChannels;
            var length = buffer.length;
            // var numSeg = Math.floor(length / 16384);
            // var padLength = 16384 * (numSeg + 1);
            var l = buffer.getChannelData(0);
            var r = channels > 1 ? buffer.getChannelData(1) : l;
            var seekingPos = null;
            var seekingDiff = 0;

            var source = {
                extract: function (target, numFrames, position) {
                    if (seekingPos != null) {
                        seekingDiff = seekingPos - position;
                        seekingPos = null;
                    }

                    position += seekingDiff;
                    // position = seekingPos;
                    // console.log(seekingDiff);
                    // console.log(position);
                    for (var i = 0; i < numFrames; i++) {
                        target[i * 2] = l[i + position];
                        target[i * 2 + 1] = r[i + position];
                    }

                    return Math.min(numFrames, length - position);
                }
            };

            var soundtouchNode;

            wavesurferTeacher.on('play', function () {
                seekingPos = ~~(wavesurferTeacher.backend.getPlayedPercents() * length);
                //console.log(seekingPos);
                // st.tempo = wavesurferTeacher.getPlaybackRate();
                st.tempo = playbackRate;

                if (st.tempo === 1) {
                    wavesurferTeacher.backend.disconnectFilters();
                } else {
                    var filter = new soundtouch.SimpleFilter(source, st);
                    soundtouchNode = soundtouch.getWebAudioNode(wavesurferTeacher.backend.ac, filter);

                    wavesurferTeacher.backend.setFilter(soundtouchNode);
                }
            });

            wavesurferTeacher.on('pause', function () {
                //soundtouchNode && soundtouchNode.disconnect();
                wavesurferTeacher.backend.disconnectFilters();
            });

            wavesurferTeacher.on('finish', function () {
                wavesurferTeacher.seekTo(0);
                //soundtouchNode && soundtouchNode.disconnect();
                wavesurferTeacher.clearRegions();
                wavesurferTeacher.disableDragSelection();
                wavesurferTeacher.backend.disconnectFilters();
                wavesurferTeacher.empty();
                wavesurferTeacher.load(audioUrl);
            });

            wavesurferTeacher.on('seek', function () {
                seekingPos = ~~(wavesurfer.backend.getPlayedPercents() * length);
                //console.log(seekingPos);
            });
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

        wavesurfer = Object.create(WaveSurfer);
        wavesurfer.init({
            container: '#wavesurf-student',
            waveColor: 'violet',
            progressColor: 'purple',
            height: '150',
            autoCenter: false,
            hideScrollbar: true,
        });
        // wavesurfer = WaveSurfer.create({
        //     container: '#wavesurf-student',
        //     waveColor: 'violet',
        //     progressColor: 'purple',
        //     height: '150',
        //     autoCenter: false,
        //     hideScrollbar: true,
        // });
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
            wavesurfer.on('region-update-end', function (region) {
                regionVar = region;
                regionPlay = "student";
                var start = region.start;
                var end = region.end;
                centerStudent = (start + end) / 2;
                if (zoomMultiStudent * zoomLevelStudent < 6400) {
                    var zoominbtn = document.getElementById("zoomin-student");
                    zoominbtn.disabled = false;
                }
                if (zoomMultiStudent != 2) {
                    var zoomoutbtn = document.getElementById("zoomout-student");
                    zoomoutbtn.disabled = false;
                }
            });
            wavesurfer.on('region-removed', function () {
                regionVar = null;
                centerStudent = 0;
                var zoominbtn = document.getElementById("zoomin-student");
                zoominbtn.disabled = true;
                if (zoomMultiStudent <= 2) {
                    var zoomoutbtn = document.getElementById("zoomout-student");
                    zoomoutbtn.disabled = true;
                }
            });

            if (recorded) {
                var audioDuration = wavesurfer.getDuration();
                zoomLevelStudent = wavesurferWidth / audioDuration;
                var downloadbtn = document.getElementById("download");
                downloadbtn.removeAttribute("disabled");
                var recordUrl = window.URL.createObjectURL(record_blob);
                downloadbtn.href = recordUrl;
                downloadbtn.download = "student_recording.wav";
            }

        });
    }
    else {
        var timeStampContainer = document.getElementsByClassName("time-stamp");
        for (var i = 0; i < timeStampContainer.length; i++) {
            if ($.isNumeric(timeStamps[i])) {
                var time = moment.unix(timeStamps[i]).format("MMM D YYYY HH:mm:ss");
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
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = true;
        var downloadbtn = document.getElementById("download");
        downloadbtn.setAttribute("disabled", "true");
        downloadbtn.removeAttribute("href");
        downloadbtn.removeAttribute("download");
        wavesurfer.empty();
        wavesurferTeacher.empty();
        if (ifTeacherLoad == true) {
            wavesurferTeacher.clearRegions();
            wavesurferTeacher.disableDragSelection();
        }
        var audioBase64 = uttrFiles["{0}_{1}".replace("{0}", goldenSpeakerName).replace("{1}", name)];
        var audioBlob = b64toBlob(audioBase64);
        audioUrl = window.URL.createObjectURL(audioBlob);
        wavesurferTeacher.load(audioUrl);
        var playbtn = document.getElementById("playPause-teacher");
        playbtn.disabled = false;
        var downloadbtn = document.getElementById("download-teacher");
        downloadbtn.removeAttribute("disabled");
        downloadbtn.href = audioUrl;
        downloadbtn.download = "{0}_{1}.wav".replace("{0}", goldenSpeakerName).replace("{1}", name);
    });
    $("#playPause-teacher").click(function () {
        if (regionVarTeacher == null) {
            wavesurferTeacher.playPause();
        }
        else {
            regionVarTeacher.play();
        }
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
        if (zoomMultiStudent != 2) {
            wavesurfer.zoom(zoomLevelStudent);
            wavesurfer.zoom(zoomLevelStudent);
            zoomMultiStudent = 2;
        }
        toggleRecordingPractice(this);
    });
    $("#playPause").click(function (){
        if (regionVar == null) {
            wavesurfer.playPause();
        }
        else {
            regionVar.play();
        }
    });
});

$(window).keydown(function(e) {
    e.stopPropagation();
    switch (e.keyCode) {
        case 32: // space key
            e.preventDefault();
            if (regionPlay == "teacher") {
                $("#playPause-teacher").trigger("click");

            }
            else {
                $("#playPause").trigger("click");
            }

            return;
        case 49: // num1 key
            if (regionPlay == "teacher") {
                var zoominbtn = document.getElementById("zoomin-teacher");
                if (zoominbtn.disabled != true) {
                    $("#zoomin-teacher").trigger("click");
                }
            }
            else {
                var zoominbtn = document.getElementById("zoomin-student");
                if (zoominbtn.disabled != true) {
                    $("#zoomin-student").trigger("click");
                }
            }

            return;
        case 51: //num3 key
            if (regionPlay == "teacher") {
                var zoomoutbtn = document.getElementById("zoomout-teacher");
                if (zoomoutbtn.disabled != true) {
                    $("#zoomout-teacher").trigger("click");
                }
            }
            else {
                var zoomoutbtn = document.getElementById("zoomout-student");
                if (zoomoutbtn.disabled != true) {
                    $("#zoomout-student").trigger("click");
                }
            }
            return;
    }

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
                else if (status == "Error") {
                    alert("An error occurs in Golden Speaker '{0}', please click resynthesize to build it again.".replace("{0}", name));
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
