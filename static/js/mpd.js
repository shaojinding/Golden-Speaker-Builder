var wavesurfer = null;
var microphone = null;
var utt_id = 0;
var repeat_id = 0;
var sentences = null;
var ALPHABET_TO_IPA_DICT = {'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AX': 'ə', 'AY': 'aɪ', 'EH': 'ɛ',
                            'ER': 'ɝ', 'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'i', 'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u',
                            'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'JH': 'dʒ',
                            'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'ɹ', 'S': 's',
                            'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'};

$(document).ready( function() {
    $("#sentence-display").html(sentences[utt_id]);

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
        var savebtn = document.getElementById("save");
        savebtn.disabled = true;
        var recordbtn = document.getElementById("record");
        recordbtn.disabled = true;
        var playPausebtn = document.getElementById("playPause");
        playPausebtn.disabled = true;
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
                fd.append('transcription', sentences[utt_id])
                fd.append('utt_id', utt_id);
                fd.append('repeat_id', repeat_id);
                $.ajax({
                    type: 'POST',
                    url: '/mpd/upload_audio/',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function () {
                    cleanDisplayMPD();
                    getTextgrid(utt_id, repeat_id);
                    repeat_id = repeat_id + 1;
                    var savebtn = document.getElementById("save");
                    savebtn.disabled = false;
                    var recordbtn = document.getElementById("record");
                    recordbtn.disabled = false;
                    var playPausebtn = document.getElementById("playPause");
                    playPausebtn.disabled = false;
                });
            }

        }
        catch (e) {
            alert("upload failed! Please try again.")
        }
    });

    $("#next").click(function (){
        utt_id = utt_id + 1;
        $("#sentence-display").html(sentences[utt_id]);
        cleanDisplayMPD();
        //document.getElementById("mpd-word").outerHTML = "";
        //document.getElementById("mpd-phoneme").outerHTML = "";
        //$("#mpd-display").css("display", "none");


        //document.getElementsByClassName("remove-ele").remove();
    });

});

function cleanDisplayMPD() {
    var node = document.getElementById("mpd-word");
        while (node.children.length > 0) {
            node.removeChild(node.children[0])
        }
        var node = document.getElementById("mpd-phoneme");
        while (node.children.length > 0) {
            node.removeChild(node.children[0])
        }
}

function getTextgrid(utt_id) {
    $.get('/mpd/get_textgrid/', {utt_id: utt_id, repeat_id: repeat_id}, function(data){
        var textgrid = JSON.parse(data);
        var word_tier = textgrid.tiers[0];
        var phoneme_tier = textgrid.tiers[1];
        var error_tier = textgrid.tiers[2];
        for (var i=0; i<word_tier.items.length; i++) {
            var word_el = $('<th class="remove-ele"></th>');// word element
            var phoneme_in_word_el = $('<td class="remove-ele"></td>');// phonemes in a td, corresponding to a word
            var word = word_tier.items[i];
            if (word.text.length != 0) {
                word_el.html(word.text);
                $('#mpd-word').append(word_el);
                for (var j=0; j<phoneme_tier.items.length; j++) {
                    var phoneme = phoneme_tier.items[j];
                    var error_flag = error_tier.items[j];
                    if (phoneme.xmin >= word.xmin && phoneme.xmax <= word.xmax && !isSil(phoneme.text)) {
                        var phoneme_el = $('<span></span>');// phoneme element
                        phoneme_el.html(phonemeNormalization(phoneme.text));
                        if (isMP(error_flag.text)) { // if it is mp, highlight it with red
                            phoneme_el.css('color', 'red');
                        }
                        phoneme_in_word_el.append(phoneme_el);
                        var space_el = $('<span></span>');
                        space_el.html(' ');
                        phoneme_in_word_el.append(space_el);
                    }
                }
                $('#mpd-phoneme').append(phoneme_in_word_el);

            }
        }
        //$("#mpd-display").css("display", "block")
        //document.getElementById("mpd-word").removeChild(this)
    });
}

// Determine if the phoneme is silence
function isSil(phoneme) {
    phoneme = phoneme.toLowerCase();
    if (phoneme === 'sil' || phoneme === '' || phoneme === 'sp' || phoneme === 'spn') {
        return true;
    }
    else {
        return false;
    }
}

// Determine if the phoneme is a mispronunciation
function isMP(text) {
    if (text === 'sub_error') {
        return true;
    }
    else {
        return false;
    }
}

// Remove the numbers in ALPHABET and convert it to IPA
function phonemeNormalization(phoneme) {
    phoneme = phoneme.replace(/[0-9]/g, '');
    return ALPHABET_TO_IPA_DICT[phoneme];
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