import React, { Suspense } from "react";
import ReactDOM from "react-dom";
import Loader from "./components/loader/Loader";

const UserCheckButton = React.lazy(() =>
	import("./components/buttons/discord/user-check-button/UserCheckButton")
);

let checkUserButton = document.getElementById("discord_check_user");
if (checkUserButton != null && checkUserButton != undefined) {
	let jCheckUserButton = $(checkUserButton);
	let jInput = $(`#${jCheckUserButton.data("related-field")}`);
	ReactDOM.render(
		<Suspense fallback={<Loader></Loader>}>
			<UserCheckButton
				url={jCheckUserButton.data("consumer-url")}
				invitationURL={jCheckUserButton.data("invitation-url")}
				relatedField={jInput}
			/>
		</Suspense>,
		checkUserButton
	);
}
