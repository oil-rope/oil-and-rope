import React, { Component } from "react";
import dayGridPlugin from "@fullcalendar/daygrid";
import FullCalendar from '@fullcalendar/react'

import "./main.scss";

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
			<FullCalendar
				data-testid="calendar"
				defaultView={this.state.defaultView}
				plugins={this.state.plugins}
				events={this.state.events}
			/>
		);
	}
}

export default Calendar;
