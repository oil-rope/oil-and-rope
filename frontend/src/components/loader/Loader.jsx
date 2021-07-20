import React from "react";
import Spinner from "react-bootstrap/Spinner";

const Loader = (text = gettext("Loading")) => {
  return (
    <div className="d-flex justify-content-around">
      <div>{`${text}...`}</div>
      <Spinner animation="border" role="status">
        <span className="sr-only">{`${text}...`}</span>
      </Spinner>
    </div>
  );
};

export default Loader;
