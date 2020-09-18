import React, { useState, useContext, useEffect, Suspense } from "react";
import Loader from "../loader/Loader";
import ChatContext from "../../contexts/ChatContext";

const Message = React.lazy(() => import("./Message"));

const MessagesContainer = () => {
	const { webSocket, setWebSocketOnMessage, chat, user } = useContext(
		ChatContext
	);
	const [userLoaded, setUserLoaded] = useState(false);
	const [messages, setMessages] = useState([]);

	/**
	 * Adds the message to messages.
	 *
	 * @param {Object} messageEvent Message received.
	 */
	const handleWebSocketOnMessage = (messageEvent) => {
		let message = JSON.parse(messageEvent.data);
		setMessages([...messages, message]);
	};

	/**
	 * Creates all messages in chat.
	 */
	const loadMessages = () => {
		if (Boolean(chat)) {
			setMessages(chat.chat_message_set);
		}
	};

	useEffect(() => {
		if (Boolean(webSocket)) {
			setWebSocketOnMessage(handleWebSocketOnMessage);
		}
	});

	useEffect(() => {
		loadMessages();
	}, [chat]);

	useEffect(() => {
		if (Boolean(user)) {
			setUserLoaded(true);
		}
	}, [user]);

	return (
		<div
			style={{
				minHeight: "300px",
				height: "400px",
				width: "100%",
				overflowY: "scroll",
			}}
		>
			{userLoaded ? (
				<Suspense fallback={<Loader />}>
					{messages.map((message, index) => (
						<Message message={message} key={index} />
					))}
				</Suspense>
			) : (
				<Loader />
			)}
		</div>
	);
};

export default MessagesContainer;
