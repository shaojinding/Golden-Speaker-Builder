/**
 * Created by dshj940428 on 10/19/2016.
 */
// phoneme substitution
$('#auto-checkboxes').bonsai({
    expandAll: false,
    checkboxes: true, // depends on jquery.qubit plugin
    createInputs: 'checkbox' // takes values from data-name and data-value, and data-name is inherited
});
var sourceModel = null;
var targetModel = null;
// var utteranceSelect = null;
var idxAdd = null;
var idxRemove = null;
// var utteranceAddSelect = null;
var utteranceNames = null;
var selectNames = [];
var selectWeeks = [];
var transcriptions = null;
var weeks = null;
var slider = null;
var disp = null;
// var phonemeArray = ['P', 'T', 'K', 'B', 'D', 'G', 'F', 'TH', 'S', 'SH', 'HH', 'V', 'DH', 'Z', 'ZH', 'CH', 'JH', 'M', 'N', 'NG', 'L', 'R', 'W', 'Y', 'IY', 'UW', 'IH', 'UH', 'EY', 'OW', 'EH', 'AH', 'AE', 'AA', 'OY', 'AY', 'AO', 'AW', 'AX', 'ER'];
var phonemeArray = ['AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'B',  'CH', 'D','DH', 'EH', 'ER', 'EY', 'F', 'G', 'HH', 'IH', 'IY', 'JH', 'K', 'L', 'M', 'N', 'NG', 'OW', 'OY', 'P', 'R', 'S', 'SH', 'T', 'TH', 'UH', 'UW', 'V', 'W', 'Y', 'Z', 'ZH'];
// var phonemeGroups = ['monophthong', 'diphthong', 'stop-v', 'fricative-v', 'affricate-v', 'nasal', 'liquid', 'glide', 'stop-uv', 'fricative-uv', 'affricate-uv'];
var selectPhonemeGroups = [];
// var chosenIndexes = [];
$(document).ready( function() {
    var audio = document.getElementById("source-play");
    var source = document.getElementById("source-play-source");
    $(".source-model").click(function () {
        $(".source-model").removeClass('active');
        sourceModel = $(this).html();
        $(this).addClass('active');
        if (targetModel != null) {
            getUtterances(audio, source);
        }
        else {
            $("#target-speaker").css("display", "inline-block")
        }
    });
    $(".target-model").click(function () {
        $(".target-model").removeClass('active');
        targetModel = $(this).html();
        $(this).addClass('active');
        if (sourceModel != null) {
            getUtterances(audio, source);
            $("#operation-div").css("display", "block");
            // $("#tempo-scale-block").css("display", "block");
            // $("#phoneme-substitution-block").css("display", "block");
        }
    });

    $("#synthesize").click(function () {
        try {
            var btnSynth = document.getElementById("synthesize");
            var checkedValue = $(".utterance-checkbox:checked").map(function () {
                return $(this).val()
            }).get();
            if (checkedValue == null  || checkedValue.length ==0) {
                alert("Please select the sentences you want to synthesize");
                return;
            }
            btnSynth.disabled = true;
            for (var i = 0; i < checkedValue.length; i++) {
                selectNames.push(utteranceNames[parseInt(checkedValue[i])]);
            }
            for (var i = 0; i < checkedValue.length; i++) {
                selectWeeks.push(weeks[parseInt(checkedValue[i])]);
            }

            var csrftoken = getCookie('csrftoken');

            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
            var fd = new FormData();
            fd.append('select_names', selectNames);
            fd.append('source_model', sourceModel);
            fd.append('target_model', targetModel);
            fd.append('select_weeks', selectWeeks);
            $.ajax({
                type: 'POST',
                url: '/speech/synthesize/',
                data: fd,
                processData: false,
                contentType: false
            }).done(function () {
                alert("Your Golden Speaker is being synthesized. Please go to 'Play with Golden Speaker' to check on the status. Once the synthesis is done, you will be able to practice with the Golden Speaker");
                window.location.href = '/speech/';
            });
        }
        catch (e) {
            alert("synthesize failed! Please try again.");
        }

    });
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

function getUtterances(audio, source) {
    $.get('/speech/get_utterances/', {source_model: sourceModel}, function(data){
        var arr = JSON.parse(data);
        utteranceNames = arr[0];
        transcriptions = arr[1];
        weeks = arr[2];
        var utterList = document.getElementById("utterance-list");
        while(utterList.firstChild){
            utterList.removeChild(utterList.firstChild);
        }
        for (var i = 0; i < transcriptions.length; i ++) {
            var node = document.createElement("A");
            var btnNode = document.createElement("BUTTON");
            btnNode.className = "btn btn-success btn-xs source-speaker-preview";
            btnNode.style.marginRight = "5px";
            btnNode.onclick = function () {
                var parent = $(this).parent();
                var innerText = parent[0].childNodes[3].data;
                var strIdx = innerText.indexOf("]");
                // var temp = innerText.substring(strIdx + 1, innerText.length);
                var childIdx = transcriptions.indexOf(innerText.substring(strIdx + 1, innerText.length));
                source.src = "/static/ARCTIC/" + sourceModel + '/test/recording/'  + utteranceNames[childIdx] + '.wav';
                audio.load();
                audio.play();
            };
            var checkbox = document.createElement('input');
            checkbox.type = "checkbox";
            checkbox.value = "{0}".replace("{0}", i);
            checkbox.className = "utterance-checkbox";
            var spaceNode = document.createTextNode("   ");
            var btnTextNode = document.createTextNode("play");
            btnNode.appendChild(btnTextNode);
            var textnode = document.createTextNode("[{}]".replace("{}", weeks[i]) + transcriptions[i]);
            node.appendChild(checkbox);
            node.appendChild(spaceNode);
            node.appendChild(btnNode);
            node.appendChild(textnode);
            node.className = 'list-group-item utterance-item';
            //document.getElementById("utterance-list").appendChild(btnNode);
            utterList.appendChild(node);
        }
        $("#utterance-block").css("display", "block");
    });
}
