import React, { Component, Suspense } from "react";
import dayGridPlugin from "@fullcalendar/daygrid";

import "./main.scss";

const FullCalendar = React.lazy(() => import("@fullcalendar/react"));

export class Calendar extends Component {
	constructor(props) {
		super(props);
		this.state = {
			events: [],
			plugins: [dayGridPlugin],
			defaultView: "dayGridMonth",
		};
	}

	render() {
		return (
			<Suspense fallback={<div>Loading...</div>}>
				<div data-testid="calendar">
					<FullCalendar
						defaultView={this.state.defaultView}
						plugins={this.state.plugins}
						events={this.state.events}
					/>
				</div>
			</Suspense>
		);
	}
}

export default Calendar;
