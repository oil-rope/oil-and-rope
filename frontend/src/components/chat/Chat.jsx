import React, { useContext, useEffect, useState } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ChatContext from "../../contexts/ChatContext";

const Chat = () => {
	const { webSocket } = useContext(ChatContext);

	const [room, setRoom] = useState(gettext("No name"));

	/**
	 * Setup all needed functions for our WebSocket.
	 */
	const setUpSocketFunctions = () => {
		webSocket.onopen = handleSocketOnOpen;
		webSocket.onclose = handleSocketOnClose;
		webSocket.onmessage = handleSocketOnMessage;
	};

	const handleSocketOnOpen = (openEvent) => {
		webSocket.send(JSON.stringify({ type: "get_user" }));
	};

	const handleSocketOnClose = (closeEvent) => {
		console.log(`${gettext("Socket closed")}.`);
	};

	const handleSocketOnMessage = (messageEvent) => {
		console.log(messageEvent);
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
		<Row>
			<Col className="bg-white">
				<h4 className="text-center">{room}</h4>
				<hr className="mx-5" />
			</Col>
		</Row>
	);
};

export default Chat;
