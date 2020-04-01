let debug = document.currentScript.getAttribute('debug');
let ws_prefix = debug === 'True' ? 'ws://' : 'wss://'
let url = ws_prefix + window.location.host + document.currentScript.getAttribute('consumer-url');

let socket = new WebSocket(url);
let btn_discord = $('#btn_discord_invite');
let btn_discord_text = btn_discord.val();
let input = $('#id_discord_id');

btn_discord.click(function (e) {
    var inputValue = input.val();

    if (inputValue != "" && inputValue != undefined) {
        data = JSON.stringify({
            type: 'check_user',
            discord_id: inputValue
        });


        try {
            socket.send(data);
            // Adding animation
            btn_discord.val('. . . ');
        } catch (e) {
            console.error(e);
        }
    }
});

socket.onmessage = function (e) {
    data = JSON.parse(e.data);

    if (data.error) {
        console.error(data.error);
    }

    if (data.exists === true) {
        btn_discord.val(gettext('Found') + '! ✓');
    } else if (data.exists === false) {
        btn_discord.val(gettext('User not found') + '! ✗');
    }
};

socket.onclose = function (e) {
    if (e.reason != "" && e.reason != null) {
        console.log("Close reason: " + e.reason);
    } else {
        console.log("No close reason given.");
    }
}
