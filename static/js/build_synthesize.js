/**
 * Created by dshj940428 on 10/19/2016.
 */
var sourceModel = null;
var targetModel = null;
// var utteranceSelect = null;
var idxAdd = null;
var idxRemove = null;
// var utteranceAddSelect = null;
var utteranceNames = null;
var selectNames = [];
var transcriptions = null;

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
        }
    });
    // $("body").on('click', 'a.utterance-item', function() {
    //     $(".utterance-item").removeClass('active');
    //     // utteranceSelect = $(this).html();
    //     idxAdd = $(this).index();
    //     $(this).addClass('active');
    //     var btnAdd = document.getElementById("add-utterance");
    //     btnAdd.disabled = false;
    // });
    // $("#add-utterance").click(function () {
    //     //var parent = document.getElementById("utterance-list");
    //     //var child1 = document.getElementById("utterance-list").firstElementChild;
    //     // var utterList = document.getElementById("utterance-list");
    //     var child = document.getElementsByClassName("utterance-item");
    //     child = child[idxAdd];
    //     var childText = child.childNodes[1];
    //     var innerText = childText.data;
    //     var childIdx = transcriptions.indexOf(innerText);
    //     selectNames.push(utteranceNames[childIdx]);
    //     // chosenIndexes.push(idxAdd);
    //     child.className = 'list-group-item added-utterance-item';
    //     document.getElementById("added-utterance-list").appendChild(child);
    //     var btnAdd = document.getElementById("add-utterance");
    //     btnAdd.disabled = true;
    //     // parent.removeChild(child);
    //     // var node = document.createElement("A");
    //     // var textnode = document.createTextNode(utteranceSelect);
    //     // node.appendChild(textnode);
    //     // node.className = 'list-group-item added-utterance-item';
    //     // document.getElementById("added-utterance-list").appendChild(node);
    // });
    // $("body").on('click', 'a.added-utterance-item', function() {
    //     $(".added-utterance-item").removeClass('active');
    //     // utteranceAddSelect = $(this).html();
    //     idxRemove = $(this).index();
    //     $(this).addClass('active');
    //     var btnRemove = document.getElementById("remove-utterance");
    //     btnRemove.disabled = false;
    // });
    // $("#remove-utterance").click(function () {
    //     var child = document.getElementsByClassName("added-utterance-item");
    //     child = child[idxRemove];
    //     // var innerText = child.innerText;
    //     // var childIdx = transcriptions.indexOf(innerText);
    //     // var removingName = utteranceNames[childIdx];
    //     selectNames.splice(idxRemove, 1);
    //     // var removingName = selectNames.pop(idxRemove);
    //     // var removingIdx = utteranceNames.indexOf(removingName);
    //     child.className = 'list-group-item utterance-item';
    //     document.getElementById("utterance-list").appendChild(child);
    //     // var utterList = document.getElementById("utterance-list");
    //     // utterList.insertBefore(child, utterList.childNodes[removingIdx + 1]);
    //     // document.getElementById("utterance-list").appendChild(child);
    //     var btnRemove = document.getElementById("remove-utterance");
    //     btnRemove.disabled = true;
    //     // var parent = document.getElementById("added-utterance-list");
    //     // var child = document.getElementById("added-utterance-list").firstElementChild;
    //     // parent.removeChild(child);
    //     // var node = document.createElement("A");
    //     // var textnode = document.createTextNode(utteranceSelect);
    //     // node.appendChild(textnode);
    //     // node.className = 'list-group-item utterance-item';
    //     //document.getElementById("utterance-list").insertBefore()
    // });
    $("#synthesize").click(function () {
        try {
            var checkedValue = $(".utterance-checkbox:checked").map(function () {
                return $(this).val()
            }).get();
            for (var i = 0; i < checkedValue.length; i++) {
                selectNames.push(utteranceNames[parseInt(checkedValue[i])]);
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
            $.ajax({
                type: 'POST',
                url: '/speech/synthesize/',
                data: fd,
                processData: false,
                contentType: false
            }).done(function () {
                alert("Your Golden Speaker is being synthesized. Please go to 'Play with Golden Speaker' to check on the status. Once the synthesis is done, you will be able to practice with the Golden Speaker");
                window.location.href = '/speech';
            });
        }
        catch (e) {
            alert("synthesize failed! Please try again.");
        }
        // try {
        //     var checkedValue = $(".utterance-checkbox:checked").map(function(){return $(this).val()}).get();
        //     var checkedValue1 = checkedValue.map(function () {return parseInt(this)}).get();
        //     var csrftoken = getCookie('csrftoken');
        //     selectNames = utteranceNames[checkedValue];
        //     $.ajaxSetup({
        //         beforeSend: function (xhr, settings) {
        //             if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        //                 xhr.setRequestHeader("X-CSRFToken", csrftoken);
        //             }
        //         }
        //     });
        //     $("#synthesize-notification").css('display', 'inline-block');
        //     var fd = new FormData();
        //     fd.append('select_names', checkedValue);
        //     fd.append('source_model', sourceModel);
        //     fd.append('target_model', targetModel);
        //     $.ajax({
        //         type: 'POST',
        //         url: '/speech/synthesize/',
        //         data: fd,
        //         processData: false,
        //         contentType: false
        //     }).done(function () {
        //         window.location.href = '/speech/practice/index'
        //     });
        // }
        // catch (e) {
        //     alert("synthesize failed! Please try again.")
        // }
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
                        var childIdx = transcriptions.indexOf(innerText);
                        source.src = "/static/ARCTIC/audio/" + sourceModel + '/'  + utteranceNames[childIdx] + '.wav';
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
                    var textnode = document.createTextNode(transcriptions[i]);
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