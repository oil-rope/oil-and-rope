import React, {
  useState,
  useContext,
  useEffect,
  useRef,
  Suspense,
} from "react";
import Loader from "../loader/Loader";

import SessionContext from "../../contexts/SessionContext";
import WebSocketContext from "../../contexts/WebSocketContext";

const Message = React.lazy(() =>
  import(/* webpackChunkName: "message" */ "./Message")
);

const MessagesContainer = () => {
  const { session } = useContext(SessionContext);
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
    if (payload.status == "error") {
      new Notification(payload.content);
    }

    if (payload.type === "send_message") {
      const message = payload.content;
      setMessages([...messages, message]);
    }

    scrollToBottom();
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

  // Okay this is tricky
  // First we check if both session and chatWebSocket exist
  useEffect(() => {
    if (Boolean(session) && Boolean(chatWebSocket)) {
      loadMessages();
    }
  }, [session, chatWebSocket]);

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
        height: "400px",
        width: "100%",
        overflowY: "scroll",
        scrollBehavior: "smooth",
      }}
      ref={messageContainerRef}
    >
      {componentLoaded ? (
        <Suspense fallback={<Loader />}>
          {messages.map((message, index) => (
            <Message message={message} key={index} />
          ))}
        </Suspense>
      ) : (
        <Loader text={gettext("Loading messages")} />
      )}
    </div>
  );
};

export default MessagesContainer;
