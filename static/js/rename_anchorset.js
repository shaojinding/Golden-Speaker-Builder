$(document).ready( function() {
    $("#rename").click(function () {
        var btn = document.getElementById('rename');
        btn.style.display = 'none';
        var p = btn.parentElement;
        var messageNode = document.createElement("P");
        var messageTextNode = document.createTextNode("renaming anchor set...");
        messageNode.appendChild(messageTextNode);
        p.appendChild(messageNode);
    })
})