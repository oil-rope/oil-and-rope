import React, { Component } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";

import "./main.scss";

export class Calendar extends Component {
	constructor(props) {
		super(props);
		this.state = {
			events: [],
		};
	}

	render() {
		return (
			<div data-testid="calendar">
				<FullCalendar
					defaultView="dayGridMonth"
					plugins={[dayGridPlugin, interactionPlugin]}
					events={this.state.events}
				/>
			</div>
		);
	}
}

export default Calendar;
