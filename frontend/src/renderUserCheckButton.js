import React from "react";
import ReactDOM from "react-dom";
import UserCheckButton from "./components/buttons/discord/UserCheckButton/UserCheckButton";
import JQuery from "jquery";

let checkUserButton = document.getElementById("discord_check_user");
if (checkUserButton != null && checkUserButton != undefined) {
	let jCheckUserButton = JQuery(checkUserButton);
	let jInput = JQuery(`#${jCheckUserButton.data("related-field")}`);
	ReactDOM.render(
		<UserCheckButton
			url={jCheckUserButton.data("consumer-url")}
			invitationURL={jCheckUserButton.data("invitation-url")}
			relatedField={jInput}
		/>,
		checkUserButton
	);
}
