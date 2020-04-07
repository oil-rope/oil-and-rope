import React, { Component, Fragment } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

export class UserCheckButton extends Component {
	constructor(props) {
		super(props);

		this.state = {
			text: `${gettext("Look for user")}!`,
			showModal: false,
			buttonDisabled: false,
		};
	}

	componentDidMount() {
		this.connector = new WebSocket(this.props.url);
		this.connector.onmessage = this.WSOnMessage;
		this.connector.onerror = this.WSOnError;
		this.connector.onclose = this.WSOnClose;
	}

	WSOnClose = (close) => {
		// Set button as disabled if WS is closed
		this.setState({ buttonDisabled: true });
	};

	WSOnError = (error) => {
		console.log(error);
	};

	WSOnMessage = (message) => {
		let { exists, error } = JSON.parse(message.data);

		if (error) {
			console.error(error);
		}

		if (exists === true) {
			this.userExists();
		} else if (exists === false) {
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
			<div data-testid="userCheckButton">
				<Fragment>
					<Button
						onClick={this.handlerClick}
						className="w-100"
						variant="info"
						disabled={this.state.buttonDisabled}
					>
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
			</div>
		);
	}
}

export default UserCheckButton;
