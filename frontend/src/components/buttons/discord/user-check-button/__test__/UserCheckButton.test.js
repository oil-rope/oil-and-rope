import React from "react";
import { render, cleanup } from "@testing-library/react";
import UserCheckButton from "../UserCheckButton";
import $ from "jquery";

// Mocking Django's gettext
global.gettext = (txt) => txt;

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
	let url = "ws://localhost";
	let invitationURL = "http://localhost";
	let relatedField = $(document.createElement("input"));
	const { getByTestId } = render(
		<UserCheckButton
			url={url}
			invitationURL={invitationURL}
			relatedField={relatedField}
		/>
	);
	expect(getByTestId("testUserCheckButton")).not.toBeNull();
});
