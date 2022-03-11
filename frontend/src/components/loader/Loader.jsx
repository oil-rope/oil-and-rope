import React from "react";
import Spinner from "react-bootstrap/Spinner";
import PropTypes from "prop-types";

const Loader = ({ text }) => (
  <div className="d-flex justify-content-around">
    <div>{`${gettext(text)}...`}</div>
    <Spinner animation="border" role="status">
      <span className="sr-only-focusable visually-hidden-focusable">{`${gettext(text)}...`}</span>
    </Spinner>
  </div>
);

Loader.propTypes = {
  text: PropTypes.string,
};

Loader.defaultProps = {
  text: "Loading",
};

export default Loader;
