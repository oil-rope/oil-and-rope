import React from "react";
import { render, cleanup } from "@testing-library/react";
import Loader from '../Loader';

// Mocking Django's gettext
global.gettext = (txt) => txt;

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
	const { getByTestId } = render(
		<Loader></Loader>
	);
	expect(getByTestId("testLoader")).not.toBeNull();
});
