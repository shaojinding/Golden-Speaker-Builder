/**
 * Created by dshj940428 on 12/16/2016.
 */
var pitchFile = null;
var wavesurfer = null;
var isRecording = false;
var regionEnabled = false;
var microphone = null;
var center = 0;
var zoomLevel = null;
var zoomMulti = 2;
var regionVar = null;
var wavesurferWidth = null;
$(document).ready( function() {
    wavesurfer = WaveSurfer.create({
        container: '#wavesurf',
        waveColor: 'violet',
        progressColor: 'purple',
        height: '150',
        autoCenter: false,
        hideScrollbar: true,
    });
    wavesurferWidth = document.getElementById("wavesurf").offsetWidth;
    wavesurfer.empty();
    var recordbtn = document.getElementById("record");
    recordbtn.disabled = false;
    var savebtn = document.getElementById("save");
    savebtn.disabled = true;
    var playbtn = document.getElementById("playPause");
    playbtn.disabled = true;
    if ((pitchFile != null) && (pitchFile != "None") ) {
        var recording_blob = b64toBlob(pitchFile);
        wavesurfer.loadBlob(recording_blob);
        wavesurfer.enableDragSelection({
            color: 'hsla(400, 100%, 30%, 0.1)',
            drag: false,
            //resize: false,
        });
        regionEnabled = true;
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = false;
        var buildbtn = document.getElementById("build-sabr-btn");
        buildbtn.disabled = false;
    }
    microphone = Object.create(WaveSurfer.Microphone);
    microphone.init({
        wavesurfer: wavesurfer
    });
    wavesurfer.on('ready', function () {
        var timeline = Object.create(WaveSurfer.Timeline);
        timeline.init({
            wavesurfer: wavesurfer,
            container: '#timeline',
            //primaryFontColor: 'white',
        });
        wavesurfer.on('region-update-end', function (region) {
            var start = region.start;
            var end = region.end;
            center = (start + end) / 2;
            if (zoomMulti * zoomLevel < 6400) {
                var zoominbtn = document.getElementById("zoomin");
                zoominbtn.disabled = false;
                // var zoomoutbtn = document.getElementById("zoomout");
                // zoomoutbtn.disabled = false;
            }
            if (zoomMulti != 2) {
                var zoomoutbtn = document.getElementById("zoomout");
                zoomoutbtn.disabled = false;
            }
            regionVar = region;
        });
        wavesurfer.on('region-removed', function () {
            regionVar = null;
            center = 0;
            var savebtn = document.getElementById("save");
            savebtn.disabled = true;
            var zoominbtn = document.getElementById("zoomin");
            zoominbtn.disabled = true;
            if (zoomMulti <= 2) {
                var zoomoutbtn = document.getElementById("zoomout");
                zoomoutbtn.disabled = true;
            }

        });
        if (!isRecording) {
            var audioDuration = wavesurfer.getDuration();
            zoomLevel = wavesurferWidth / audioDuration;
            if (regionVar != null && zoomMulti * zoomLevel < 6400) {
                var zoominbtn = document.getElementById("zoomin");
                zoominbtn.disabled = false;
                // var zoomoutbtn = document.getElementById("zoomout");
                // zoomoutbtn.disabled = false;
            }
            var playbtn = document.getElementById("playPause");
            playbtn.disabled = false;
        }
    });
    $("#record").click(function (){
        if (zoomMulti != 2) {
            wavesurfer.zoom(zoomLevel);
            wavesurfer.zoom(zoomLevel);
            zoomMulti = 2;
        }
        toggleRecordingPitch(this);
    });
    $("#playPause").click(function (){
        if (regionVar == null) {
            wavesurfer.playPause();
        }
        else {
            regionVar.play();
        }
    });
    $("#zoomin").click(function () {
        var sec = wavesurfer.getDuration();
        wavesurfer.seekTo(center / sec);
        wavesurfer.zoom(zoomMulti * zoomLevel);
        zoomMulti = zoomMulti * 2;
        if (zoomMulti * zoomLevel >= 6400) {
            var zoominbtn = document.getElementById("zoomin");
            zoominbtn.disabled = true;
        }
        var zoomoutbtn = document.getElementById("zoomout");
        zoomoutbtn.disabled = false;
    });
    $("#zoomout").click(function () {
        var sec = wavesurfer.getDuration();
        wavesurfer.seekTo(center / sec);
        wavesurfer.zoom(zoomLevel);
        wavesurfer.zoom(zoomLevel);
        zoomMulti = 2;
        var zoominbtn = document.getElementById("zoomin");
        zoominbtn.disabled = false;
        var zoomoutbtn = document.getElementById("zoomout");
        zoomoutbtn.disabled = true;
        //wavesurfer.scrollParent = false;
    });
    $("#save").click(function () {
        try {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
            var fd = new FormData();
            var reader = new window.FileReader();
            reader.readAsDataURL(record_blob);
            reader.onloadend = function () {
                base64data = reader.result;
                var base64blob = base64data.substring(22, base64data.length);
                fd.append('recording', base64blob);
                $.ajax({
                    type: 'POST',
                    url: '/speech/upload_pitch/',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function () {
                    $("#status").html('saved');
                    var savebtn = document.getElementById("save");
                    savebtn.disabled = true;
                    var recordbtn = document.getElementById("record");
                    recordbtn.disabled = true;
                    var playbtn = document.getElementById("playPause");
                    playbtn.disabled = true;
                    $("#SoundRecorder").hide();
                    $("#Passage").hide();
                    $("#instruction").text("Please click Finish to build the Anchor Set.");
                    var buildbtn = document.getElementById("build-sabr-btn");
                    buildbtn.disabled = false;
                });
            }


        }
        catch (e) {
            alert("upload failed! Please try again.")
        }
    });


});


$(window).keydown(function(e) {
    e.stopPropagation();
    switch (e.keyCode) {
        case 32: // space key
            e.preventDefault();
            $("#playPause").trigger("click");
            return;
        case 49: // num1 key
            var zoominbtn = document.getElementById("zoomin");
            if (zoominbtn.disabled != true) {
                $("#zoomin").trigger("click");
            }
            return;
        case 51: //num3 key
            var zoomoutbtn = document.getElementById("zoomout");
            if (zoomoutbtn.disabled != true) {
                $("#zoomout").trigger("click");
            }
            return;
        // case 82: // "r" key
        //     $("#record").trigger("click");
        //     return;
        // case 83: // "s" key
        //     $("#save").trigger("click");
        //     return;
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
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
