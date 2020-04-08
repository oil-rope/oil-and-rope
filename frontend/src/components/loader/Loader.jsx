import React from "react";
import Spinner from "react-bootstrap/Spinner";

function Loader() {
	return (
		<div data-testid="testLoader" className="d-flex justify-content-around">
			<div>{`${gettext("Loading")}...`}</div>
			<Spinner animation="border" role="status">
				<span className="sr-only">{`${gettext("Loading")}...`}</span>
			</Spinner>
		</div>
	);
}

export default Loader;
