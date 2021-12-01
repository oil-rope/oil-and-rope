/**
 * @jest-environment jsdom
 */

import React from "react";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";

import MessagesContainer from "./MessagesContainer";

describe("tests for MessagesContainer", () => {
	beforeAll(() => {
		global.gettext = (text) => text;
	});

	test("should renders without messages", () => {
		const component = render(<MessagesContainer />);

		expect(component).not.toBeNull();
	});
});
