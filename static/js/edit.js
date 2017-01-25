/**
 * Created by Burning on 9/13/2016.
 */
var wavesurfer = null;
var microphone = null;
var regionEnabled = false;
var startTime = null;
var endTime = null;
var centerTime = null;
var currentPhoneme = null;
var lastPhoneme = null;
var zoomLevel = null;
var zoomMulti = 2;
var audioDuration = null;
var wavesurferWidth = null;
var saveSuccess = false;
var savedPhonemeCount = 0;
var numPhoneme = 24;
var phonemeArray = ['P', 'T', 'K', 'B', 'D', 'G', 'F', 'TH', 'S', 'SH', 'HH', 'V', 'DH', 'Z', 'ZH', 'CH', 'JH', 'M', 'N', 'NG', 'L', 'R', 'W', 'Y']
var record_details = null;
var firstTimeLoad = true;
var ifRecordNewAudio = false;
$(document).ready( function() {
    document.getElementById("nav_ac").className += 'active';
    for (var i = 0; i < numPhoneme; i++) {
        document.getElementById(phonemeArray[i]).className = 'phoneme btn btn-xs btn-success';
    }
    if (currentPhoneme != null && currentPhoneme != "index") {
        document.getElementById(currentPhoneme).className = 'phoneme btn btn-xs btn-primary';
    }
    var recordbtn = document.getElementById("record");
    recordbtn.disabled = true;
    var zoominbtn = document.getElementById("zoomin");
    zoominbtn.disabled = true;
    var zoomoutbtn = document.getElementById("zoomout");
    zoomoutbtn.disabled = true;
    var savebtn = document.getElementById("save");
    savebtn.disabled = true;
    var playbtn = document.getElementById("playPause");
    playbtn.disabled = true;
    wavesurfer = WaveSurfer.create({
        container: '#wavesurf',
        waveColor: 'violet',
        progressColor: 'purple',
        height: '150',
    });
    if (currentPhoneme == null || currentPhoneme == "index") {
        wavesurfer.empty();
        $("#startTime").html("0.00");
        $("#endTime").html("0.00");
        $("#status").html('unsaved');
    }
    else {
        $("#startTime").html(record_details[0]);
        $("#endTime").html(record_details[1]);
        $("#status").html('unsaved');
        wavesurferWidth = document.getElementById("wavesurf").offsetWidth;
        var recording_blob = b64toBlob(record_details[3]);
        wavesurfer.loadBlob(recording_blob)
        microphone = Object.create(WaveSurfer.Microphone);
        microphone.init({
            wavesurfer: wavesurfer
        });
    }

    wavesurfer.on('ready', function () {
        var timeline = Object.create(WaveSurfer.Timeline);
        timeline.init({
            wavesurfer: wavesurfer,
            container: '#timeline',
            //primaryFontColor: 'white',
        });
        if (firstTimeLoad) {
            wavesurfer.enableDragSelection({
                color: 'hsla(400, 100%, 30%, 0.1)',
                drag: false,
                //resize: false,
            });
            wavesurfer.addRegion({
                start: record_details[0], // time in seconds
                end: record_details[1], // time in seconds
                color: 'hsla(400, 100%, 30%, 0.1)'
            });
            regionEnabled = true;
            firstTimeLoad = false
        }
        wavesurfer.on('region-updated', function (region) {
            var start = region.start;
            var end = region.end;
            centerTime = ((start + end) / 2).toFixed(2);
            startTime = start.toFixed(2);
            endTime = end.toFixed(2)
            $("#startTime").html(startTime);
            $("#endTime").html(endTime);
            audioDuration = wavesurfer.getDuration();
            zoomLevel = wavesurferWidth / audioDuration;
            var zoominbtn = document.getElementById("zoomin");
            zoominbtn.disabled = false;
            var zoomoutbtn = document.getElementById("zoomout");
            zoomoutbtn.disabled = false;
            var savebtn = document.getElementById("save");
            savebtn.disabled = false;
        });
        wavesurfer.on('region-click', function (region, e) {
            e.stopPropagation();
            // Play on click, loop on shift click
            e.shiftKey ? region.playLoop() : region.play();

            //region.color = 'hsla(100, 100%, 70%, 0.1)';

        });
    });


    $("#record").click(function (){
        toggleRecording(this);
        ifRecordNewAudio = true;
    });
    $("#playPause").click(function (){
        wavesurfer.playPause();
        $(this).toggleClass("playing");
    });
    $(".phoneme").click(function () {
        var me = $(this);
        var jumpPhoneme = me.text()
        window.location.href = '/speech/edit/{0}'.replace('{0}', jumpPhoneme)


    });
    // var zoominbtn = document.getElementById("zoomin");
    $("#zoomin").click(function () {
        wavesurfer.zoom(zoomMulti * zoomLevel);
        zoomMulti = zoomMulti * 2;
        if (zoomMulti * zoomLevel >= 6400) {
            var zoominbtn = document.getElementById("zoomin");
            zoominbtn.disabled = true;
        }
    });
    $("#zoomout").click(function () {
        wavesurfer.zoom(zoomLevel);
        zoomMulti = 2;
        var zoominbtn = document.getElementById("zoomin");
        zoominbtn.disabled = false;
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
            fd.append('L', startTime);
            fd.append('R', endTime);
            fd.append('C', centerTime);
            fd.append('phoneme', currentPhoneme);
            fd.append('if_record_new_audio', ifRecordNewAudio);
            var reader = new window.FileReader();
            if (ifRecordNewAudio) {
                reader.readAsDataURL(record_blob);
                reader.onloadend = function () {
                    base64data = reader.result;
                    var base64blob = base64data.substring(22, base64data.length)
                    fd.append('recording', base64blob);
                    $.ajax({
                        type: 'POST',
                        url: '/speech/upload_edit_annotation/',
                        data: fd,
                        processData: false,
                        contentType: false
                    }).done(function () {
                        $("#status").html('saved');
                        var savebtn = document.getElementById("save");
                        savebtn.disabled = true;
                        var zoominbtn = document.getElementById("zoomin");
                        zoominbtn.disabled = true;
                        var zoomoutbtn = document.getElementById("zoomout");
                        zoomoutbtn.disabled = true;
                        var recordbtn = document.getElementById("record");
                        recordbtn.disabled = true;
                        var playbtn = document.getElementById("playPause");
                        playbtn.disabled = true;
                    });
                }
            }
            else {
                $.ajax({
                    type: 'POST',
                    url: '/speech/upload_edit_annotation/',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function () {
                    $("#status").html('saved');
                    var savebtn = document.getElementById("save");
                    savebtn.disabled = true;
                    var zoominbtn = document.getElementById("zoomin");
                    zoominbtn.disabled = true;
                    var zoomoutbtn = document.getElementById("zoomout");
                    zoomoutbtn.disabled = true;
                    var recordbtn = document.getElementById("record");
                    recordbtn.disabled = true;
                    var playbtn = document.getElementById("playPause");
                    playbtn.disabled = true;
                });
            }

        }
        catch (e) {
            alert("upload failed! Please try again.")
        }
    });
    // var saveinbtn = document.getElementById("save");
    // saveinbtn.click(function () {


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
// function upload(blob) {
//     // var fd = new FormData();
//     //     fd.append('data', soundBlob);
//     var csrftoken = getCookie('csrftoken');
//         var fd = {CSRF: csrftoken, record_audio: record_blob}
//         $.ajax({
//             type: 'POST',
//             url: '/speech/upload_record',
//             data: fd,
//             processData: false,
//             contentType: false
//         });
// }
// function upload(blob) {
//     var csrftoken = getCookie('csrftoken');
//
//     var xhr = new XMLHttpRequest();
//     xhr.open('POST', '/speech/upload_record/', true);
//     xhr.setRequestHeader("X-CSRFToken", csrftoken);
//     xhr.setRequestHeader("phoneme", currentPhoneme);
//
//
//     xhr.send(blob);
//     var res = xhr.responseText;
// }



// function initWaveSurfer () {
//     wavesurfer.on('ready', function () {
//         if (!regionEnabled) {
//             wavesurfer.enableDragSelection({
//                 color: 'hsla(100, 100%, 30%, 0.1)',
//                 drag: false,
//                 //resize: false,
//             });
//             regionEnabled = true;
//
//         }
//
//         //if (regionsEnabled != true) {
//         //    wavesurfer.enableDragSelection({
//         //        color: 'hsla(100, 100%, 30%, 0.1)',
//         //    });
//         //
//         //}
//
//         // $("#spectrogram").css("display", "inline-block");
//         // var spectrogram = Object.create(WaveSurfer.Spectrogram);
//         // spectrogram.init({
//         //     wavesurfer: wavesurfer,
//         //     container: "#spectrogram",
//         //     //container: "#SoundExample",
//         //
//         // });
//     });
//     wavesurfer.on('region-click', function (region, e) {
//         e.stopPropagation();
//         // Play on click, loop on shift click
//         e.shiftKey ? region.playLoop() : region.play();
//         var start = region.start;
//         var end = region.end;
//         //region.color = 'hsla(100, 100%, 70%, 0.1)';
//         $("#startTime").html(start.toFixed(2));
//         $("#endTime").html(end.toFixed(2));
//     });
//     //wavesurfer.on('region-dblclick', function (region, e) {
//     //    e.stopPropagation();
//     //    region.remove();
//     //    //var start = region.start;
//     //    //var end = region.end;
//     //    //$("#startTime").html(start);
//     //    //$("#endTime").html(end);
//     //});
// }