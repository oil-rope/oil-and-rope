import React, { useContext, useEffect, useState } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import ChatContext from "../../contexts/ChatContext";
import ChatInput from "./ChatInput";

const Chat = () => {
	const { webSocket } = useContext(ChatContext);

	const [room, setRoom] = useState(gettext("No name"));
	const [messages, setMessages] = useState([]);

	/**
	 * Setup all needed functions for our WebSocket.
	 */
	const setUpSocketFunctions = () => {
		webSocket.onopen = handleSocketOnOpen;
		webSocket.onclose = handleSocketOnClose;
		webSocket.onmessage = handleSocketOnMessage;
	};

	const handleSocketOnOpen = (openEvent) => {};

	const handleSocketOnClose = (closeEvent) => {};

	const handleSocketOnMessage = (messageEvent) => {
		let message = JSON.parse(messageEvent.data);
		setMessages([...messages, message.content.content]);
	};

	useEffect(() => {
		if (Boolean(webSocket)) {
			setUpSocketFunctions();
		}
	});

	useEffect(() => {
		if (Boolean(webSocket)) {
			setUpSocketFunctions();
		}
	}, [webSocket]);

	return (
		<Container fluid={true} className="bg-white p-5">
			<h4 className="text-center">{room}</h4>
			<hr className="mx-5" />
			<Row>
				<Col style={{ minHeight: "300px", width: "100%" }}>
					{messages.map((message, index) => (
						<Row
							key={index}
							className="justify-content-end"
							style={{ minHeight: "50px" }}
						>
							<Col
								xs={7}
								className="bg-info border"
								style={{ borderRadius: "10px" }}
							>
								<span>{message}</span>
							</Col>
						</Row>
					))}
				</Col>
			</Row>
			<Row>
				<Col>
					<ChatInput />
				</Col>
			</Row>
		</Container>
	);
};

export default Chat;
