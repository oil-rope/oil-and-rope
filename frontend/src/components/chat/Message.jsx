import React, { useContext, Fragment } from "react";
import { Row, Col } from "react-bootstrap";

import AuthContext from "../../contexts/AuthContext";

import { formatDate } from "../../utils/date.js";

const Message = ({ message }) => {
  const { user } = useContext(AuthContext);
  const colWidthXS = 10;
  const colWidthMD = 8;

  const renderMessage = () => {
    return (
      <Fragment>
        <p className="mb-0">
          <small className="text-white font-weight-bold">
            <u>{message.author.username}</u>
          </small>
          <br />
          {message.message}
        </p>
        <p className="text-right mb-0">
          <small className="text-muted">
            {gettext("Sent at")} {formatDate(message.entry_created_at)}
          </small>
        </p>
      </Fragment>
    );
  };

  if (message.author.id == user.id) {
    return (
      <Row
        className="justify-content-end m-0 mb-2"
        style={{ minHeight: "50px" }}
      >
        <Col
          xs={colWidthXS}
          md={colWidthMD}
          className="bg-extra border"
          style={{ borderRadius: "10px" }}
        >
          {renderMessage()}
        </Col>
      </Row>
    );
  } else {
    return (
      <Row
        className="justify-content-start m-0 mb-2"
        style={{ minHeight: "50px" }}
      >
        <Col
          xs={colWidthXS}
          md={colWidthMD}
          className="bg-info border"
          style={{ borderRadius: "10px" }}
        >
          {renderMessage()}
        </Col>
      </Row>
    );
  }
};

export default Message;
