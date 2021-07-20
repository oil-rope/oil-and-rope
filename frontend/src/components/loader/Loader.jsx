import React from "react";
import Spinner from "react-bootstrap/Spinner";
import PropTypes from "prop-types";

const Loader = ({ text = "Loading" }) => {
  return (
    <div className="d-flex justify-content-around">
      <div>{`${gettext(text)}...`}</div>
      <Spinner animation="border" role="status">
        <span className="sr-only">{`${gettext(text)}...`}</span>
      </Spinner>
    </div>
  );
};

Loader.propTypes = {
  text: PropTypes.string,
};

export default Loader;
