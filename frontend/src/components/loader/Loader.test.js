/**
 * @jest-environment jsdom
 */

import React from "react";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import Loader from "./Loader.jsx";

// Mocking Django's gettext
global.gettext = (txt) => txt;

describe("Loader renderizations", () => {
	test("renders component", () => {
		const component = render(<Loader />);
		component.getAllByText("Loading...");
	});

	test("render component with text", () => {
		const loadingText = "Loading component";
		const component = render(<Loader text={loadingText} />);
		component.getAllByText(`${loadingText}...`);
	});
});
