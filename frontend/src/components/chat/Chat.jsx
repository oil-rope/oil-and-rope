import React, { Suspense, useEffect, useContext } from "react";
import Axios from "axios";

import { Container, Row, Col } from "react-bootstrap";

import AuthContext from "../../contexts/AuthContext.jsx";
import SessionContext from "../../contexts/SessionContext.jsx";
import WebSocketContext from "../../contexts/WebSocketContext.jsx";

import Loader from "../loader/Loader.jsx";

import { resolveURL } from "../../utils/api.js";

const MessagesContainer = React.lazy(() =>
  import(/* webpackChunkName: "messagescontainer" */ "./MessagesContainer")
);
const ChatInput = React.lazy(() =>
  import(/* webpackChunkName: "chatinput" */ "./ChatInput")
);

const Chat = () => {
  const { user } = useContext(AuthContext);
  const { session, chat, setChat } = useContext(SessionContext);
  const { chatWebSocket } = useContext(WebSocketContext);

  const getChat = () => {
    resolveURL("api:chat:chat-detail", { pk: session.chat }).then((url) => {
      Axios.get(`${url}?use_map=chat_message_set`)
        .then((res) => res.data)
        .then(setChat);
    });
  };

  const handleOnOpen = (ev) => {
    if (process.env.NODE_ENV === "development" || false) {
      console.debug(ev);
    }
  };

  const handleOnClose = (ev) => {
    if (process.env.NODE_ENV === "development" || false) {
      console.debug(ev);
    }
  };

  const setUpChannelLayer = () => {
    if (chatWebSocket.readyState == chatWebSocket.OPEN) {
      chatWebSocket.send(
        JSON.stringify({
          type: "setup_channel_layer",
          token: user.auth_token,
          chat: chat.id,
        })
      );
    }
  };

  const setUpWebSocket = () => {
    chatWebSocket.onopen = handleOnOpen;
    chatWebSocket.onclose = handleOnClose;
  };

  useEffect(() => {
    if (chatWebSocket) {
      setUpWebSocket();
    }
  }, [chatWebSocket]);

  useEffect(() => {
    if (session) {
      getChat();
    }
  }, [session]);

  useEffect(() => {
    if (chat) {
      setUpChannelLayer();
    }
  }, [chat]);

  return (
    <Container fluid className="bg-white pb-4">
      <Row>
        <Col>
          <Suspense fallback={<Loader />}>
            <MessagesContainer />
          </Suspense>
        </Col>
      </Row>
      <Row className="mt-5">
        <Col>
          <Suspense fallback={<Loader />}>
            <ChatInput />
          </Suspense>
        </Col>
      </Row>
    </Container>
  );
};

export default Chat;
