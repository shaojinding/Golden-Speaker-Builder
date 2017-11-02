/**
 * Created by dshj940428 on 10/19/2016.
 */
var name = null;
var built = null;
var buildingAnchorSet = null;
var timeStamps = null;
$(document).ready( function() {
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
});

function checkBuildStatus() {
    if (buildingAnchorSet!=null) {
        for (var i = 0; i < buildingAnchorSet.length; i++) {
            $.get('/speech/get_build_status/', {slug: buildingAnchorSet[i]}, function (data) {
                var arr = JSON.parse(data);
                name = arr[0];
                built = arr[1];
                if (built == "Built") {
                    alert("Your anchor set '{0}' is built!".replace("{0}", name));
                    window.location.href = '/speech/manage_anchorset'
                }
                else if (built == "Error") {
                    alert("An error occurs in anchor set '{0}', please click rebuild to build it again.".replace("{0}", name));
                    window.location.href = '/speech/manage_anchorset'
                }
            });
        }
        setTimeout("checkBuildStatus()", 30000);
    }

}

/*
function rename(name) {
    var anchorsetName = document.getElementById("anchorset-entry-" + name);
    var defaultText = anchorsetName.innerHTML;

    var inputNode = document.createElement("INPUT");
    inputNode.name = 'generated_input';
    inputNode.style.display = "inline-block";
    inputNode.style.height = "20px";
    inputNode.value = defaultText;
    inputNode.id = "input-name";
    var btnNode = document.createElement("BUTTON");
    btnNode.className = "btn btn-success btn-xs";
    btnNode.style.display = "inline-block";
    btnNode.onclick = function (name) {
        // something to upload the new name, because it is hard to validate the form, we abandon it temporally.
    };
    var btnTextNode = document.createTextNode("Accept");
    btnNode.appendChild(btnTextNode);

    anchorsetName.innerHTML = "";
    anchorsetName.appendChild(inputNode);
    var anchorsetOption = document.getElementById("option-" + name);
    while (anchorsetOption.firstChild) {
        anchorsetOption.removeChild(anchorsetOption.firstChild);
    }
    anchorsetOption.appendChild(btnNode);
    document.getElementById("anchorset-entry-" + name).firstChild.select();
}

function confirmRename() {
    
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
}*/
