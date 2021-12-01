import React, {
  useState,
  useContext,
  useEffect,
  useRef,
  Suspense,
} from "react";
import { scrollToBottom } from "../../utils/ux";

import SessionContext from "../../contexts/SessionContext";
import WebSocketContext from "../../contexts/WebSocketContext";

import Loader from "../loader/Loader";

const Message = React.lazy(() =>
  import(/* webpackChunkName: "message" */ "./Message")
);

const MessagesContainer = () => {
  const { chat } = useContext(SessionContext);
  const { chatWebSocket } = useContext(WebSocketContext);

  const [messages, setMessages] = useState(null);
  const [componentLoaded, setComponentLoaded] = useState(false);

  const messageContainerRef = useRef(null);

  /**
   * Adds the message to messages.
   *
   * @param {Object} messageEvent Message received.
   */
  const handleWebSocketOnMessage = (messageEvent) => {
    const payload = JSON.parse(messageEvent.data);
    if (payload.status === "error") {
      Notification(payload.content);
    }

    if (payload.type === "send_message") {
      const message = payload.content;
      setMessages([...messages, message]);
    }

    scrollToBottom(messageContainerRef);
  };

  /**
   * Creates all messages in chat.
   */
  const loadMessages = () => {
    setMessages(chat.chat_message_set);
  };

  // Okay this is tricky
  // First we check if both session and chatWebSocket exist
  useEffect(() => {
    if (Boolean(chat) && Boolean(chatWebSocket)) {
      loadMessages();
    }
  }, [chatWebSocket, chat]);

  // Once they exist we set the onmessage and set component as loaded
  useEffect(() => {
    if (messages !== null) {
      chatWebSocket.onmessage = handleWebSocketOnMessage;
      setComponentLoaded(true);
    }
  }, [messages]);

  return (
    <div
      style={{
        minHeight: "400px",
        height: "100%",
        width: "100%",
        overflowY: "scroll",
        scrollBehavior: "smooth",
      }}
      ref={messageContainerRef}
      className="p-2"
    >
      {componentLoaded ? (
        <Suspense fallback={<Loader />}>
          {messages.map((message, index) => (
            <Message message={message} key={`msgIdx${index + 10}`} />
          ))}
        </Suspense>
      ) : (
        <Loader text={gettext("Loading messages")} />
      )}
    </div>
  );
};

export default MessagesContainer;
