import React from "react";
import { Suspense, lazy } from 'react';
import ReactDOM from "react-dom";
import Chat from "./components/chat/Chat";

let chat = document.getElementById('chat_room_index')
ReactDOM.render(<Chat />, chat);

if (chat != null && chat != undefined) {
    let url = 'ws://localhost:8000/chat/'


}
// consumer_url = 'ws://localhost:8000/ws/
// consumer_url += 'localhost:8000'
// consumer_url += reverse('bot:ws_bot_register')
// return consumer_url