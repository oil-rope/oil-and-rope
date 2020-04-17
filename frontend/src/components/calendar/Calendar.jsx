import React, { Component } from "react";
import dayGridPlugin from "@fullcalendar/daygrid";
import FullCalendar from "@fullcalendar/react";

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
			<div data-testid="testCalendar">
				<FullCalendar
					defaultView={this.state.defaultView}
					plugins={this.state.plugins}
					events={this.state.events}
				/>
			</div>
		);
	}
}

export default Calendar;
