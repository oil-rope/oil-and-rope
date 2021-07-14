import React, { Suspense, useState, useEffect } from "react";
import { Container, Row, Col } from "react-bootstrap";

import WebSocketContext from "../../contexts/WebSocketContext.jsx";
import Loader from "../loader/Loader.jsx";

const Chat = React.lazy(() => import("../chat/Chat.jsx"));

const App = () => {
  const [chatWebSocket, setChatWebSocket] = useState(null);

  return (
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
  );
};

export default App;
