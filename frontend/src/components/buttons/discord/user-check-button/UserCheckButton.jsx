import React, { Component, Fragment } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import axios from "axios";
import Cookies from "js-cookie";

export class UserCheckButton extends Component {
	constructor(props) {
		super(props);

		this.state = {
			text: `${gettext("Look for user")}!`,
			showModal: false,
			buttonDisabled: true,
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": Cookies.get("csrftoken"),
			},
		};
	}

	componentDidMount() {
		this.connector = new WebSocket(this.props.url);
		this.connector.onopen = this.WSOnOpen;
		this.connector.onmessage = this.WSOnMessage;
		this.connector.onerror = this.WSOnError;
		this.connector.onclose = this.WSOnClose;
	}

	WSOnOpen = (open) => {
		// Set button as enabled
		this.setState({ buttonDisabled: false });
	};

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

	// TODO: Maybe we could change this to WebSocket?
	handleCreateInvitation = () => {
		let discord_user_id = this.props.relatedField.val();
		axios
			.post(
				this.props.sendInvitationURL,
				{
					discord_user_id: discord_user_id,
				},
				{ headers: this.state.headers }
			)
			.then(() => {
				this.setState({
					text: `${gettext(
						"Once you accept the invitation click here again to search your user"
					)}.`,
				});
			})
			.catch((err) => {
				console.error(err);
				this.setState({
					text: `${gettext("We couldn't sent you a message")}.
								 ${gettext("Do you share server with our bot?")}`,
				});
			});
		this.handleClose();
	};

	handleClose = () => this.setState({ showModal: false });
	handleShow = () => this.setState({ showModal: true });

	render() {
		return (
			<div data-testid="testUserCheckButton">
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
							<p>
								{`${gettext("Seems like this user doesn't exists")}.`}
								<br />
								{`${gettext(
									"Have you invited the bot to your server and requested and invitation?"
								)}`}
								<br />
								<span className="text-muted">
									{`${gettext(
										"Please note that you have to share at least one server with our bot"
									)}.`}
								</span>
							</p>
						</Modal.Body>
						<Modal.Footer>
							<Button variant="primary" onClick={this.handleCreateInvitation}>
								{gettext("Send invitation")}
							</Button>
							<Button variant="extra" onClick={this.handleInvite}>
								{gettext("Invite Bot")}
							</Button>
							<Button variant="secondary" onClick={this.handleClose}>
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
