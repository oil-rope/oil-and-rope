import React from "react";
import { render, cleanup } from "@testing-library/react";
import UserCheckButton from "../UserCheckButton";

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
	const { getByTestId } = render(<UserCheckButton />);
	expect(getByTestId("userCheckButton")).not.toBeNull();
});
