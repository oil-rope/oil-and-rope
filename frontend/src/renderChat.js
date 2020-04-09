import React from "react";
import { Suspense, lazy } from 'react';
import ReactDOM from "react-dom";
import Chat from "./components/chat/Chat";

let chat = document.getElementById('chat_room_index')
ReactDOM.render(<Chat />, chat);
