import React, { Suspense, useEffect, useContext } from "react";
import Axios from "axios";

import { Container, Row, Col } from "react-bootstrap";

import AuthContext from "../../contexts/AuthContext";
import SessionContext from "../../contexts/SessionContext";
import WebSocketContext from "../../contexts/WebSocketContext";

import Loader from "../loader/Loader";

import { resolveURL } from "../../utils/api";

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

  const handleOnOpen = () => undefined;

  const handleOnClose = () => undefined;

  const setUpChannelLayer = () => {
    if (chatWebSocket.readyState === chatWebSocket.OPEN) {
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
    <Container fluid className="bg-light pb-4">
      <Row>
        <Col>
          <Suspense fallback={<Loader />}>
            <MessagesContainer />
          </Suspense>
        </Col>
      </Row>
      <Row className="pt-3">
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
