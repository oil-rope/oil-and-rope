import React from "react";
import { render, cleanup } from "@testing-library/react";
import Calendar from "../Calendar";
import "@testing-library/jest-dom/extend-expect";

// Mocking Django's gettext
global.gettext = (txt) => txt;

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
	const { getByTestId } = render(<Calendar />);
	expect(getByTestId("testCalendar")).not.toBeNull();
});
