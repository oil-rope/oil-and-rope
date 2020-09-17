import React, { Fragment, Suspense, useEffect, useState } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ChatContext from "../../contexts/ChatContext";
import Loader from "../loader/Loader";
import Chat from "./Chat";

const App = ({ socketURL = null }) => {
	const [webSocket, setWebSocket] = useState(null);
	const defaultContextValue = {
		webSocket: webSocket,
	};

	useEffect(() => {
		let webSocket = new WebSocket(socketURL);
		setWebSocket(webSocket);
	}, []);

	return (
		<Fragment>
			<ChatContext.Provider value={defaultContextValue}>
				<Row>
					<Col>
						<Suspense fallback={<Loader />}>
							<Chat />
						</Suspense>
					</Col>
				</Row>
			</ChatContext.Provider>
		</Fragment>
	);
};

export default App;
