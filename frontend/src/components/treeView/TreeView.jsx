import React, { Component } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getPlaces } from "../../actions/places";

export class TreeView extends Component {
	static propTypes = {
		places: PropTypes.array.isRequired,
	};

	componentDidMount() {
		this.props.getPlaces();
	}

	render() {
		return <div></div>;
	}
}

const mapStateToProps = (state) => ({
	places: state.places.places,
});

export default connect(mapStateToProps, { getPlaces })(TreeView);
