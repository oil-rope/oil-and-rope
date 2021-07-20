import React from "react";
import { render, cleanup } from "@testing-library/react";
import Loader from "../Loader.jsx";

// Mocking Django's gettext
global.gettext = (txt) => txt;

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
	const { getByTestId } = render(<Loader />);
	expect(getByTestId("testLoader")).not.toBeNull();
});
