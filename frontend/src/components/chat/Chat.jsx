import React, { Suspense } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import Loader from "../loader/Loader";

const MessagesContainer = React.lazy(() => import("./MessagesContainer"));
const ChatInput = React.lazy(() => import("./ChatInput"));

const Chat = () => {
	return (
		<Container fluid={true} className="bg-white pb-4">
			<Row>
				<Col>
					<Suspense fallback={<Loader />}>
						<MessagesContainer />
					</Suspense>
				</Col>
			</Row>
			<Row className="mt-5">
				<Col>
					<Suspense fallback={<Loader />}>
						<ChatInput />
					</Suspense>
				</Col>
			</Row>
		</Container>
	);
};

export default Chat;
