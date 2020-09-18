import React, { useContext } from "react";
import { Row, Col } from "react-bootstrap";
import ChatContext from "../../contexts/ChatContext";

const Message = ({ message }) => {
	const { user } = useContext(ChatContext);
	const colWidthXS = 10;
	const colWidthMD = 8;

	if (message.author == user.id) {
		return (
			<Row className="justify-content-end m-0" style={{ minHeight: "50px" }}>
				<Col
					xs={colWidthXS}
					md={colWidthMD}
					className="bg-extra border"
					style={{ borderRadius: "10px" }}
				>
					<span>{message.message}</span>
				</Col>
			</Row>
		);
	} else {
		return (
			<Row className="justify-content-start m-0" style={{ minHeight: "50px" }}>
				<Col
					xs={colWidthXS}
					md={colWidthMD}
					className="bg-info border"
					style={{ borderRadius: "10px" }}
				>
					<span>{message.message}</span>
				</Col>
			</Row>
		);
	}
};

export default Message;
