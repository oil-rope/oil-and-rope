import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import ChatInput from "./ChatInput";
import MessagesContainer from "./MessagesContainer";

const Chat = () => {
	return (
		<Container fluid={true} className="bg-white pb-4">
			<Row>
				<Col>
					<MessagesContainer />
				</Col>
			</Row>
			<Row className="mt-5">
				<Col>
					<ChatInput />
				</Col>
			</Row>
		</Container>
	);
};

export default Chat;
