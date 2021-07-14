import React, { Suspense, useState, useEffect, useContext } from "react";
import { Container, Row, Col } from "react-bootstrap";

import WebSocketContext from "../../contexts/WebSocketContext.jsx";
import Loader from "../loader/Loader.jsx";

import AuthContext from "../../contexts/AuthContext.jsx";

const MessagesContainer = React.lazy(() => import("./MessagesContainer"));
const ChatInput = React.lazy(() => import("./ChatInput"));

const Chat = () => {
  const [connection, setConnection] = useState(null);
  const [handleOnMessage, setHandleOnMessage] = useState(null);

  const { userToken } = useContext(AuthContext);

  const setUpChannel = () => {
    connection.send(
      JSON.stringify({
        type: "setup_channel_layer",
        token: userToken,
        chat: 123,
      })
    );
  };

  const setUpWebSocket = () => {
    if (connection !== null && connection !== undefined) {
      connection.onclose = handleOnClose;
      connection.onmessage = handleOnMessage;
      setUpChannel();
    }
  };

  const handleOnClose = (ev) => {
    console.error(ev);
  };

  useEffect(() => {
    let connection = new WebSocket("ws://localhost:8000/ws/chat/");
    setConnection(connection);
  }, []);

  useEffect(() => {
    setUpWebSocket();
  }, [connection]);

  return (
    <WebSocketContext.Provider value={{ connection, setHandleOnMessage }}>
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
    </WebSocketContext.Provider>
  );
};

export default Chat;
