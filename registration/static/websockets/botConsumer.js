var debug = document.currentScript.getAttribute('debug');
var ws_prefix = debug === 'True' ? 'ws://' : 'wss://'
var url = ws_prefix + window.location.host + document.currentScript.getAttribute('consumer-url');

var socket = new WebSocket(url);

$('#btn_discord_invite').click(function (e) {
    var input = $('#id_discord_id').val();
    data = JSON.stringify({
        type: 'check_user',
        discord_id: input
    });

    socket.send(data);
});

socket.onmessage = function (e) {
    data = JSON.parse(e.data);

    if (data.error) {
        console.error(data.error);
    }

    if (data.exists) {
        console.log('User exists!');
    } else {
        console.log('User does not exist.');
    }
};

socket.onclose = function (e) {
    if (e.reason != "" && e.reason != null) {
        console.log("Close reason: " + e.reason);
    } else {
        console.log("No close reason given.");
    }
}
