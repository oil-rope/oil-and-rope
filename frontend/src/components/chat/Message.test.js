/**
 * @jest-environment jsdom
 */

import React from "react";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import Message from "./Message";
import AuthContext from "../../contexts/AuthContext";

describe("tests for messages", () => {
	let user;
	let anotherUser;
	let message;

	beforeAll(() => {
		global.gettext = (text) => text;
	});

	beforeEach(() => {
		user = { id: 1, username: "TestUser" };
		anotherUser = { id: 2, username: "UserTest" };
		message = {
			message: "Random message",
			author: user,
			entry_created_at: "2021-01-01 00:00:00",
		};
	});

	test("should render correctly with message", () => {
		const component = render(
			<AuthContext.Provider value={{ user }}>
				<Message message={message} />
			</AuthContext.Provider>
		);
		component.getByText("Random message");
		expect(component).not.toBeNull();
	});

	test("should not render without message", () => {
		expect(() => render(<Message />)).toThrowError(
			/Cannot read property 'author' of undefined$/
		);
	});

	test("should render not extra color if not author", () => {
		const component = render(
			<AuthContext.Provider value={{ user: anotherUser }}>
				<Message message={message} />
			</AuthContext.Provider>
		);
		component.getByText("Random message");
		expect(component.container.querySelector(".bg-secondary")).toBeNull();
	});

	test("should render extra color if author", () => {
		const component = render(
			<AuthContext.Provider value={{ user }}>
				<Message message={message} />
			</AuthContext.Provider>
		);
		component.getByText("Random message");
		expect(component.container.querySelector(".bg-secondary")).not.toBeNull();
	});
});
