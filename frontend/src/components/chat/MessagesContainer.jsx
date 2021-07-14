import React, {
  useState,
  useContext,
  useEffect,
  useRef,
  Suspense,
} from "react";
import Loader from "../loader/Loader";
import ChatContext from "../../contexts/ChatContext";

const Message = React.lazy(() => import("./Message"));

const MessagesContainer = () => {
  const { webSocket, setWebSocketOnMessage, chat, user } =
    useContext(ChatContext);
  const [userLoaded, setUserLoaded] = useState(false);
  const [messages, setMessages] = useState([]);
  const messageContainerRef = useRef(null);

  /**
   * Adds the message to messages.
   *
   * @param {Object} messageEvent Message received.
   */
  const handleWebSocketOnMessage = (messageEvent) => {
    let payload = JSON.parse(messageEvent.data);
    let message = payload.message;
    setMessages([...messages, message]);

    if (payload.hasOwnProperty("error")) {
      new Notification(payload.error);
      scrollToBottom();
    }
  };

  /**
   * Creates all messages in chat.
   */
  const loadMessages = () => {
    if (Boolean(chat)) {
      setMessages(chat.chat_message_set);
    }
  };

  /**
   * Scrolls to bottom.
   */
  const scrollToBottom = () => {
    let element = messageContainerRef.current;
    element.scrollTop = element.scrollHeight;
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

  useEffect(() => {
    scrollToBottom();
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
