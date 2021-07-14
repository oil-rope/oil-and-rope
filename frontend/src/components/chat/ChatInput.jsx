import React, { useContext, useState } from "react";
import { Form, Col, Button } from "react-bootstrap";

import WebSocketContext from "../../contexts/WebSocketContext.jsx";
import SessionContext from "../../contexts/SessionContext.jsx";

const ChatInput = () => {
  const [message, setMessage] = useState(null);
  const func = "send_message";

  const { chatWebSocket } = useContext(WebSocketContext);
  const { session } = useContext(SessionContext);

  /**
   * Declares what to do on submit.
   *
   * @param {SyntheticEvent} e Event dispatched at submit.
   */
  const handleFormOnSubmit = (e) => {
    e.preventDefault();
    if (Boolean(message)) {
      chatWebSocket.send(
        JSON.stringify({
          type: func,
          message: message,
          chat: session.chat.id,
        })
      );
      e.currentTarget.reset();
    }
  };

  return (
    <Form onSubmit={handleFormOnSubmit}>
      <Form.Row>
        <Col xs={9} lg={10}>
          <Form.Control
            type="text"
            placeholder={`${gettext("Start typing")}...`}
            onChange={(e) => setMessage(e.target.value)}
          />
        </Col>
        <Col xs={3} lg={2}>
          <Button className="w-100" variant="primary" type="submit">
            <i className="ic ic-send" />
          </Button>
        </Col>
      </Form.Row>
    </Form>
  );
};

export default ChatInput;
