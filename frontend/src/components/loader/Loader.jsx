import React, { Component, Fragment } from "react";
import Spinner from "react-bootstrap/Spinner";

export class Loader extends Component {
	render() {
		return (
			<div className="d-flex justify-content-around">
				<div>{`${gettext("Loading")}...`}</div>
				<Spinner animation="border" role="status">
					<span className="sr-only">{`${gettext("Loading")}...`}</span>
				</Spinner>
			</div>
		);
	}
}

export default Loader;
