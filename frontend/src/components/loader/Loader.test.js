/**
 * @jest-environment jsdom
 */

import React from "react";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import Loader from "./Loader";

// Mocking Django's gettext
global.gettext = (txt) => txt;

describe("Loader renderizations", () => {
	test("renders component", () => {
		const component = render(<Loader />);
		component.getAllByText("Loading...");

		expect(component).not.toBeNull();
	});

	test("render component with text", () => {
		const loadingText = "Loading component";
		const component = render(<Loader text={loadingText} />);
		component.getAllByText(`${loadingText}...`);

		expect(component).not.toBeNull();
	});
});
