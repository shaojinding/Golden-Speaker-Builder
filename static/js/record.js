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
// var audioDuration = null;
var wavesurferWidth = null;
var saveSuccess = false;
var savedPhonemeCount = 0;
var numPhoneme = 40;
var consArray = ['P', 'T', 'K', 'B', 'D', 'G', 'F', 'TH', 'S', 'SH', 'HH', 'V', 'DH', 'Z', 'ZH', 'CH', 'JH', 'M', 'N', 'NG', 'L', 'R', 'W', 'Y']
var vowArray = ['IY', 'UW', 'IH', 'UH', 'EY', 'OW', 'EH', 'AH', 'AE', 'AA', 'OY', 'AY', 'AO', 'AW', 'AX', 'ER'];
var savedPhoneme = null;
var record_details = null;
var firstTimeLoad = true;
var reRecord = false;
var regionVar = null;
var isRecording = false;
var Ipas = null;
var Keywords = null;
var center = 0;
$(document).ready( function() {
    var finishPercent = savedPhoneme.length / numPhoneme;
    $("#record-progress-bar").css('width', (finishPercent * 100).toString() + "%");
    $("#record-progress-bar").text(Math.round(finishPercent * 100).toString() + "%");
    if (currentPhoneme == "index") {
        $("#consTable").css("display", "block");
        $("#SoundRecorder").hide();
        $("#info-panel").hide();
    }
    else {
        var cp = $("#{0}".replace("{0}", currentPhoneme)).text();
        $("#phoneme-info").html("Phoneme: {0}".replace("{0}", cp));
        var keyword = Keywords[Ipas.indexOf(cp)];
        $("#word-info").html("Key word: {0}".replace("{0}", keyword));
        window.scrollTo(0,document.body.scrollHeight);
    }
    if ($.inArray(currentPhoneme, consArray) >= 0) {
        $("#consTable").css("display", "block");
        $("#vowelTable").css("display", "none");
        $("#consTab").addClass("active");
        $("#vowelTab").removeClass("active");
    }
    if ($.inArray(currentPhoneme, vowArray) >= 0) {
        $("#consTable").css("display", "none");
        $("#vowelTable").css("display", "block");
        $("#vowelTab").addClass("active");
        $("#consTab").removeClass("active");
    }
    //document.getElementById("nav_ac").className += 'active';
    for (var i = 0; i < savedPhoneme.length; i++) {
        document.getElementById(savedPhoneme[i]).className = 'phoneme btn btn-xs btn-success';
        var btn = document.getElementById(savedPhoneme[i]);
    }
    if (currentPhoneme != null && currentPhoneme != "index") {
        document.getElementById(currentPhoneme).className = 'phoneme btn btn-xs btn-primary';
    }
    // if ($.inArray(currentPhoneme, consArray) >= 0) {
    //     $("#consTable").css("display", "block");
    //     $("#vowelTable").css("display", "none");
    //     $(this).addClass("active");
    //     $("#vowelTab").removeClass("active");
    // }
    // if ($.inArray(currentPhoneme, vowArray) >= 0) {
    //     $("#consTable").css("display", "none");
    //     $("#vowelTable").css("display", "block");
    //     $(this).addClass("active");
    //     $("#consTab").removeClass("active");
    // }
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
    if ($.inArray(currentPhoneme, savedPhoneme) >= 0) {
        var start = Number(record_details[0]);
        var end = Number(record_details[1]);
        center = (start + end) / 2;
        $("#startTime").html(record_details[0]);
        $("#endTime").html(record_details[1]);
        wavesurferWidth = document.getElementById("wavesurf").offsetWidth;
        var recording_blob = b64toBlob(record_details[3]);
        wavesurfer.loadBlob(recording_blob);
        var recordbtn = document.getElementById("record");
        recordbtn.disabled = false;
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = false;
        // wavesurfer.empty();
        microphone = Object.create(WaveSurfer.Microphone);
        microphone.init({
            wavesurfer: wavesurfer
        });
    }
    else {
        $("#startTime").html('0.00');
        $("#endTime").html('0.00');
        var recordbtn = document.getElementById("record");
        if (currentPhoneme == "index") {
            recordbtn.disabled = true;
        }
        else {
            recordbtn.disabled = false;
        }
        var zoominbtn = document.getElementById("zoomin");
        zoominbtn.disabled = true;
        var zoomoutbtn = document.getElementById("zoomout");
        zoomoutbtn.disabled = true;
        var savebtn = document.getElementById("save");
        savebtn.disabled = true;
        var playbtn = document.getElementById("playPause");
        playbtn.disabled = true;
        microphone = Object.create(WaveSurfer.Microphone);
        microphone.init({
            wavesurfer: wavesurfer
        });

    }


    // wavesurfer.load("/static/audio/test.wav");
    wavesurfer.on('ready', function () {
        var timeline = Object.create(WaveSurfer.Timeline);
        timeline.init({
            wavesurfer: wavesurfer,
            container: '#timeline',
            //primaryFontColor: 'white',
        });
        if ($.inArray(currentPhoneme, savedPhoneme) >=0 && firstTimeLoad) {
            wavesurfer.enableDragSelection({
                color: 'hsla(400, 100%, 30%, 0.1)',
                drag: false,
                //resize: false,
            });
            regionVar = wavesurfer.addRegion({
                start: record_details[0], // time in seconds
                end: record_details[1], // time in seconds
                color: 'hsla(400, 100%, 30%, 0.1)',
                drag: false
            });
            regionEnabled = true;
            firstTimeLoad = false
        }
        wavesurfer.on('click', function (e) {
            e.stopImmediatePropagation();
        });
        wavesurfer.on('region-update-end', function (region) {
            start = region.start;
            end = region.end;
            center = (start + end) / 2;
            centerTime = ((start + end) / 2).toFixed(2);
            startTime = start.toFixed(2);
            endTime = end.toFixed(2);
            $("#startTime").html(startTime);
            $("#endTime").html(endTime);
            var savebtn = document.getElementById("save");
            savebtn.disabled = false;
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
            $("#startTime").html('0.00');
            $("#endTime").html('0.00');
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

    $("#consTab").click(function () {
        $("#consTable").css("display", "block");
        $("#vowelTable").css("display", "none");
        $("#pitchTable").css("display", "none");
        $(this).addClass("active");
        $("#vowelTab").removeClass("active");
        $("#pitchTab").removeClass("active");
    });

    $("#vowelTab").click(function () {
        $("#consTable").css("display", "none");
        $("#vowelTable").css("display", "block");
        $("#pitchTable").css("display", "none");
        $(this).addClass("active");
        $("#consTab").removeClass("active");
        $("#pitchTab").removeClass("active");
    });

    // $("#pitchTab").click(function () {
    //     $("#consTable").css("display", "none");
    //     $("#vowelTable").css("display", "none");
    //     $("#pitchTable").css("display", "block");
    //     $(this).addClass("active");
    //     $("#vowelTab").removeClass("active");
    //     $("#consTab").removeClass("active");
    // });

    $("#record").click(function (){
        if (zoomMulti != 2) {
            wavesurfer.zoom(zoomLevel);
            zoomMulti = 2;
            //wavesurfer.scrollParent = false;
        }
        //$(this).toggleClass("blink_me");
        toggleRecording(this);
    });
    $("#playPause").click(function (){
        if (regionVar == null) {
            wavesurfer.playPause();
        }
        else {
            regionVar.play();
        }

    });
    $(".phoneme").click(function () {
        var jumpPhoneme = $(this).attr('id');
        window.location.href = '/speech/record/{0}'.replace('{0}', jumpPhoneme);
    });
    // var zoominbtn = document.getElementById("zoomin");
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
            fd.append('L', startTime);
            fd.append('R', endTime);
            fd.append('C', centerTime);
            fd.append('phoneme', currentPhoneme);
            fd.append('re_record', reRecord);
            if (reRecord == false && $.inArray(currentPhoneme, savedPhoneme) >=0) {
                // if ($.inArray(currentPhoneme, savedPhoneme) >=0) {
                $.ajax({
                    type: 'POST',
                    url: '/speech/upload_annotation/',
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
                    $("#info-panel").hide();
                    $("#SoundRecorder").hide();
                    document.getElementById(currentPhoneme).className = 'phoneme btn btn-xs btn-success';
                    if (savedPhoneme.length >= numPhoneme - 1) {
                        var nextbtn = document.getElementById("btn_next");
                        nextbtn.disabled = false;
                        $("#btn_next").css("display", "inline-block");
                    }
                });
            }
            else {
                var reader = new window.FileReader();
                reader.readAsDataURL(record_blob);
                reader.onloadend = function () {
                    base64data = reader.result;
                    var base64blob = base64data.substring(22, base64data.length);
                    fd.append('recording', base64blob);
                    $.ajax({
                        type: 'POST',
                        url: '/speech/upload_annotation/',
                        data: fd,
                        processData: false,
                        contentType: false
                    }).done(function () {
                        var phonemebtn = document.getElementById(currentPhoneme);
                        phonemebtn.className = 'phoneme btn btn-xs btn-success';
                        var savebtn = document.getElementById("save");
                        savebtn.disabled = true;
                        var zoominbtn = document.getElementById("zoomin");
                        zoominbtn.disabled = true;
                        var zoomoutbtn = document.getElementById("zoomout");
                        zoomoutbtn.disabled = true;
                        var playbtn = document.getElementById("playPause");
                        playbtn.disabled = true;
                        $("#info-panel").hide();
                        $("#SoundRecorder").hide();
                        document.getElementById(currentPhoneme).className = 'phoneme btn btn-xs btn-success';
                        if (savedPhoneme.length >= numPhoneme - 1) {
                            var nextbtn = document.getElementById("btn_next");
                            nextbtn.disabled = false;
                            $("#btn_next").css("display", "inline-block");
                        }
                        var finishPercent = (savedPhoneme.length + 1) / numPhoneme;
                        $("#record-progress-bar").css('width', (finishPercent * 100).toString() + "%");
                        $("#record-progress-bar").text(Math.round(finishPercent * 100).toString() + "%");
                    });
                }
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