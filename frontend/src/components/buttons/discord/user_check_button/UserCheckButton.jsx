import React, { Component, Fragment } from "react";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";

export class UserCheckButton extends Component {
	constructor(props) {
		super(props);

		this.state = {
			text: `${gettext("Look for user")}!`,
			showModal: false,
		};
		this.connector = new WebSocket(props.url);
	}

	componentDidMount() {
		this.connector.onmessage = this.WSOnMessage;
	}

	WSOnMessage = (message) => {
		let data = JSON.parse(message.data);

		if (data.error) {
			console.error(data.error);
		}

		if (data.exists === true) {
			this.userExists();
		} else if (data.exists === false) {
			this.userDoesNotExist();
		}
	};

	handlerClick = () => {
		let data = JSON.stringify({
			type: "check_user",
			discord_id: this.props.relatedField.val(),
		});
		this.connector.send(data);
		this.setState({ text: ". . ." });
	};

	userExists = () => {
		this.setState({
			text: `${gettext("Found")}! ✓`,
		});
	};

	userDoesNotExist = () => {
		this.setState({
			text: `${gettext("User not found")}! ✗`,
		});
		this.handleShow();
	};

	handleInvite = () => {
		window.open(this.props.invitationURL, "_blank");
		this.handleClose();
	};

	handleClose = () => this.setState({ showModal: false });
	handleShow = () => this.setState({ showModal: true });

	render() {
		return (
			<Fragment>
				<Button onClick={this.handlerClick} className="w-100" variant="info">
					{this.state.text}
				</Button>
				<Modal show={this.state.showModal} onHide={this.handleClose}>
					<Modal.Header closeButton>
						<Modal.Title>{`${gettext("User not found")}! ✗`}</Modal.Title>
					</Modal.Header>
					<Modal.Body>
						{`${gettext("Seems like this user doesn't exists")}.`}
						<br />
						{`${gettext("Have you invited the bot to your server?")}`}
					</Modal.Body>
					<Modal.Footer>
						<Button variant="extra" onClick={this.handleInvite}>
							{gettext("Invite")}
						</Button>
						<Button variant="primary" onClick={this.handleClose}>
							{gettext("Close")}
						</Button>
					</Modal.Footer>
				</Modal>
			</Fragment>
		);
	}
}

export default UserCheckButton;
