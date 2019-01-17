var wavesurfer = null;
var microphone = null;
var utt_id = 0;

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

        wavesurfer.on('click', function (e) {
            e.stopImmediatePropagation();
        });

    });

    $("#record").click(function (){
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
                var base64data = reader.result;
                var base64blob = base64data.substring(22, base64data.length);
                fd.append('recording', base64blob);
                $.ajax({
                    type: 'POST',
                    url: '/mpd/upload_audio/',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function () {
                    getTextgrid(utt_id);
                    utt_id = utt_id + 1;
                });
            }

        }
        catch (e) {
            alert("upload failed! Please try again.")
        }
    });

});

function getTextgrid(utt_id) {
    $.get('/mpd/get_textgrid/', {utt_id: utt_id}, function(data){
        var textgrid = JSON.parse(data);
    });
}

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