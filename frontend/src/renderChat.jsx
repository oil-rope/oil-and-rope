import React from "react";
import ReactDOM from "react-dom";
import App from "./components/chat/App";

let currentScript = document.currentScript;
let element = document.querySelector(
	currentScript.getAttribute("data-renderer")
);
let wsURL = currentScript.getAttribute("data-socket");

ReactDOM.render(
	<App socketURL={`ws://${window.location.host}${wsURL}`} />,
	element
);
