import React, { useState, useEffect, Suspense } from "react";
import { Container, Row, Col } from "react-bootstrap";

import WebSocketContext from "../../contexts/WebSocketContext";
import SessionContext from "../../contexts/SessionContext";

import Loader from "../loader/Loader";

import * as Constants from "../../utils/constants";
import { getSession } from "./utils";

const Chat = React.lazy(() =>
  import(/* webpackChunkName: "chat" */ "../chat/Chat")
);

const App = () => {
  const [session, setSession] = useState(null);
  const [chat, setChat] = useState(null);
  const [chatWebSocket, setChatWebSocket] = useState(null);

  const setUpChatWebSocket = () => {
    setChatWebSocket(new WebSocket(Constants.WS_CHAT));
  };

  useEffect(() => {
    getSession().then((res) => setSession(res.data));
    setUpChatWebSocket();
  }, []);

  return (
    <SessionContext.Provider value={{ session, chat, setChat }}>
      <Container fluid className="px-0">
        <WebSocketContext.Provider value={{ chatWebSocket }}>
          <Row>
            <Col xs={12} lg={8} />
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
