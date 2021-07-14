import React, { Suspense, useEffect, useContext } from "react";
import { Container, Row, Col } from "react-bootstrap";

import AuthContext from "../../contexts/AuthContext.jsx";
import SessionContext from "../../contexts/SessionContext.jsx";
import WebSocketContext from "../../contexts/WebSocketContext.jsx";
import Loader from "../loader/Loader.jsx";

const MessagesContainer = React.lazy(() => import("./MessagesContainer"));
const ChatInput = React.lazy(() => import("./ChatInput"));

const Chat = () => {
  const { user } = useContext(AuthContext);
  const { session } = useContext(SessionContext);
  const { chatWebSocket } = useContext(WebSocketContext);

  const handleOnOpen = (ev) => {
    return;
  };

  const handleOnClose = (ev) => {
    return;
  };

  const setUpChannelLayer = () => {
    if (chatWebSocket.readyState == chatWebSocket.OPEN && Boolean(session)) {
      chatWebSocket.send(
        JSON.stringify({
          type: "setup_channel_layer",
          token: user.auth_token,
          chat: session.chat.id,
        })
      );
    }
  };

  const setUpWebSocket = () => {
    if (Boolean(chatWebSocket)) {
      chatWebSocket.onopen = handleOnOpen;
      chatWebSocket.onclose = handleOnClose;
    }
  };

  useEffect(() => {
    setUpWebSocket();
  }, []);

  useEffect(() => {
    setUpWebSocket();
  }, [chatWebSocket]);

  useEffect(() => {
    setUpChannelLayer();
  }, [session]);

  return (
    <Container fluid={true} className="bg-white pb-4">
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
