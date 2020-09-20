import React from "react";
import ReactDOM from "react-dom";
import App from "./components/chat/App";

let currentScript = document.currentScript;
let element = document.querySelector(
	currentScript.getAttribute("data-renderer")
);
let wsURL = currentScript.getAttribute("data-socket");
let chatInfoURL = currentScript.getAttribute("data-chat-info");
let userURL = currentScript.getAttribute("data-user-url");

ReactDOM.render(
	<App socketURL={wsURL} chatURL={chatInfoURL} userURL={userURL} />,
	element
);
