import React, { Fragment, Suspense, useEffect, useState } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ChatContext from "../../contexts/ChatContext";
import Loader from "../loader/Loader";
import Chat from "./Chat";
import Axios from "axios";

const App = ({ socketURL, chatURL, userURL }) => {
	const [webSocket, setWebSocket] = useState(null);
	const [chat, setChat] = useState(null);
	const [user, setUser] = useState(null);

	/**
	 * Substides onMessage func.
	 *
	 * @param {Function} func Function to substitude onMessage.
	 */
	const setWebSocketOnMessage = (func) => {
		webSocket.onmessage = func;
	};

	/**
	 * Substitudes onOpen func.
	 *
	 * @param {Function} func Function to substide onOpen.
	 */
	const setWebSocketOnOpen = (func) => {
		webSocket.onopen = func;
	};

	/**
	 * Loads Chat Object from URL
	 */
	const loadChat = () => {
		Axios.get(chatURL)
			.then((res) => {
				setChat(res.data);
			})
			.catch((err) => console.error(err));
	};

	/**
	 * Loads logged user object.
	 */
	const loadUser = () => {
		Axios.get(userURL)
			.then((res) => {
				setUser(res.data);
			})
			.catch((err) => console.error(err));
	};

	useEffect(() => {
		let webSocket = new WebSocket(socketURL);
		setWebSocket(webSocket);
		loadChat();
		loadUser();
	}, []);

	const defaultContextValue = {
		webSocket: webSocket,
		chat: chat,
		user: user,
		setWebSocketOnMessage: setWebSocketOnMessage,
		setWebSocketOnOpen: setWebSocketOnOpen,
	};

	return (
		<Fragment>
			<ChatContext.Provider value={defaultContextValue}>
				<Row>
					<Col>
						<Suspense fallback={<Loader />}>
							<Chat />
						</Suspense>
					</Col>
				</Row>
			</ChatContext.Provider>
		</Fragment>
	);
};

export default App;
