import React, { useState, useContext, useEffect, Suspense } from "react";
import Loader from "../loader/Loader";

import SessionContext from "../../contexts/SessionContext";
import WebSocketContext from "../../contexts/WebSocketContext";

const Message = React.lazy(() => import("./Message"));

const MessagesContainer = () => {
  const { session } = useContext(SessionContext);
  const { chatWebSocket } = useContext(WebSocketContext);

  const [messages, setMessages] = useState([]);

  /**
   * Adds the message to messages.
   *
   * @param {Object} messageEvent Message received.
   */
  const handleWebSocketOnMessage = (messageEvent) => {
    const payload = JSON.parse(messageEvent.data);
    if (payload.status == "error") {
      new Notification(payload.content);
      scrollToBottom();
    }

    if (payload.type === "send_message") {
      const message = payload.content;
      setMessages([...messages, message]);
    }
  };

  /**
   * Creates all messages in chat.
   */
  const loadMessages = () => {
    setMessages(session.chat.chat_message_set);
  };

  /**
   * Scrolls to bottom.
   */
  const scrollToBottom = () => {
    let element = messageContainerRef.current;
    element.scrollTop = element.scrollHeight;
  };

  useEffect(() => {
    if (Boolean(chatWebSocket)) {
      chatWebSocket.onmessage = handleWebSocketOnMessage;
    }
  }, []);

  useEffect(() => {
    if (Boolean(session)) {
      loadMessages();
    }
  }, [session]);

  return (
    <div
      style={{
        height: "400px",
        width: "100%",
        overflowY: "scroll",
        scrollBehavior: "smooth",
      }}
    >
      <Suspense fallback={<Loader />}>
        {messages.map((message, index) => (
          <Message message={message} key={index} />
        ))}
      </Suspense>
    </div>
  );
};

export default MessagesContainer;
