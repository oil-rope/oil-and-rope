import React, { useState, useEffect, Suspense } from "react";
import { Container, Row, Col } from "react-bootstrap";

import WebSocketContext from "../../contexts/WebSocketContext.jsx";
import SessionContext from "../../contexts/SessionContext.jsx";

import Loader from "../loader/Loader.jsx";

import * as Constants from "../../utils/constants.js";
import { getSession } from "./utils.js";

const Chat = React.lazy(() => import("../chat/Chat.jsx"));

const App = () => {
  const [session, setSession] = useState(null);
  const [chatWebSocket, setChatWebSocket] = useState(null);

  const setUpChatWebSocket = () => {
    setChatWebSocket(new WebSocket(Constants.WS_CHAT));
  };

  useEffect(() => {
    getSession().then((res) => setSession(res.data));
    setUpChatWebSocket();
  }, []);

  return (
    <SessionContext.Provider value={{ session }}>
      <Container>
        <WebSocketContext.Provider value={{ chatWebSocket }}>
          <Row>
            <Col xs={12} lg={8}></Col>
            <Col xs={12} lg={4}>
              <Suspense fallback={<Loader text={gettext("Loading chat")} />}>
                <Chat />
              </Suspense>
            </Col>
          </Row>
        </WebSocketContext.Provider>
      </Container>
    </SessionContext.Provider>
  );
};

export default App;
