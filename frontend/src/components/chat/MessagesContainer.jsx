import React, { useState, useContext, useEffect } from "react";
import Loader from "../loader/Loader";
import ChatContext from "../../contexts/ChatContext";
import Message from "./Message";

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
		let messageResponse = JSON.parse(messageEvent.data);
		let message = messageResponse.message;
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
				messages.map((message) => (
					<Message message={message} key={message.id} />
				))
			) : (
				<Loader />
			)}
		</div>
	);
};

export default MessagesContainer;
