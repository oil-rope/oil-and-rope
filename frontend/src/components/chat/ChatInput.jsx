import React, { useContext, useState } from "react";
import { Form, Col, Button } from "react-bootstrap";
import ChatContext from "../../contexts/ChatContext";

const ChatInput = () => {
	const { webSocket } = useContext(ChatContext);
	const [message, setMessage] = useState(null);
	const func = "send_message";

	/**
	 * Declares what to do on submit.
	 *
	 * @param {SyntheticEvent} e Event dispatched at submit.
	 */
	const handleFormOnSubmit = (e) => {
		e.preventDefault();
		if (Boolean(message)) {
			webSocket.send(
				JSON.stringify({
					type: func,
					content: message,
				})
			);
			e.currentTarget.reset();
		}
	};

	return (
		<Form onSubmit={handleFormOnSubmit}>
			<Form.Row>
				<Col xs={10}>
					<Form.Control
						type="text"
						placeholder={`${gettext("Start typing")}...`}
						onChange={(e) => setMessage(e.target.value)}
					/>
				</Col>
				<Col xs={2}>
					<Button className="w-100" variant="primary" type="submit">
						<i className="ic ic-send"></i>
					</Button>
				</Col>
			</Form.Row>
		</Form>
	);
};

export default ChatInput;
