$(document).ready( function() {
    $("#copy").click(function () {
        var btn = document.getElementById('copy');
        btn.style.display = 'none';
        var p = btn.parentElement;
        var messageNode = document.createElement("P");
        var messageTextNode = document.createTextNode("copying anchor set...");
        messageNode.appendChild(messageTextNode);
        p.appendChild(messageNode);
    })
})