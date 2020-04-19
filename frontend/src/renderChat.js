import React from "react";
import { Suspense, lazy } from 'react';
import ReactDOM from "react-dom";
import Loader from "./components/loader/Loader";
import Chat from "./components/chat/Chat";

let chat = document.getElementById('chat_room_index')

if (chat != null && chat != undefined) {
    ReactDOM.render(
        <Suspense fallback={<Loader></Loader>}>
            <Chat/>
        </Suspense>,
    chat
    );
}