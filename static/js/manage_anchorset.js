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

