/**
 * Created by dshj940428 on 10/19/2016.
 */
var slug = null;
var name = null;
var built = null;
var checkBuildStatusId = null;
$(document).ready( function() {
    //checkBuildStatusId = setInterval ( "checkBuildStatus()", 1000 );
});

function checkBuildStatus() {
    $.get('/speech/get_build_status/', {slug: slug}, function(data){
        var arr = JSON.parse(data);
        name = arr[0];
        built = arr[1];
        if (built == "Built") {
            alert ( "Your anchor set '{0}' is built!".replace("{0}", name) );
            clearInterval ( checkBuildStatusId );
        }
    });

}

