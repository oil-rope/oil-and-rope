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

	const App = () => {
		return (
			<>
				<Suspense fallback={<Loader />}>
					<UserCheckButton
						url={jCheckUserButton.data("consumer-url")}
						invitationURL={jCheckUserButton.data("invitation-url")}
						sendInvitationURL={jCheckUserButton.data("send-invitation-url")}
						relatedField={jInput}
					/>
				</Suspense>
			</>
		);
	};

	ReactDOM.render(<App />, checkUserButton);
}
