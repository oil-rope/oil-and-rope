import React from "react";
import { Suspense, lazy } from 'react';
import ReactDOM from "react-dom";
import Loader from "./components/loader/Loader";
import Messages from "./components/messages/Messages";

let messages = document.getElementById('chat-log');
let user = $("#chat-log").attr('data-user');
console.log(user);
console.log("not available")

if (messages != null && messages != undefined) {
    console.log("not available")

    ReactDOM.render(
        <Suspense fallback={<Loader></Loader>}>
            <Messages user={user}/>
        </Suspense>,
    messages,

    );
}
else {
    console.log("not available")
}