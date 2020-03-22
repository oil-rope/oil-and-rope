var url = 'ws://' + window.location.host + document.currentScript.getAttribute('consumer-url');
var socket = new WebSocket(url);
$('#btn_discord_invite').click(function (e) {
    var input = $('#id_discord_id').val();
    socket.send(input);
});
socket.onmessage = function (e) {
    console.log(e.data);
};
