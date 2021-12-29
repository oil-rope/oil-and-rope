import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Row, Col } from "react-bootstrap";

import AuthContext from "../../contexts/AuthContext";

import { formatDate } from "../../utils/date";

const Message = ({ message }) => {
  const { user } = useContext(AuthContext);
  const colWidthXS = 10;
  const colWidthMD = 8;

  const renderMessage = () => (
    <>
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
    </>
  );

  if (message.author.id === user.id) {
    return (
      <Row
        className="justify-content-end m-0 mb-2"
        style={{ minHeight: "50px" }}
      >
        <Col
          xs={colWidthXS}
          md={colWidthMD}
          className="bg-secondary border"
          style={{ borderRadius: "10px" }}
        >
          {renderMessage()}
        </Col>
      </Row>
    );
  }

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
};

Message.propTypes = {
  message: PropTypes.shape({
    author: PropTypes.shape({
      id: PropTypes.number.isRequired,
      username: PropTypes.string.isRequired,
    }),
    message: PropTypes.string,
    entry_created_at: PropTypes.string,
  }).isRequired,
};

export default Message;
