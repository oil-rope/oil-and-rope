import React, { useState } from "react";
import dayGridPlugin from "@fullcalendar/daygrid";
import FullCalendar from "@fullcalendar/react";

const Calendar = () => {
	const [plugins, setPlugins] = useState([dayGridPlugin]);
	const [defaultView, setDefaultView] = useState("dayGridMonth");
	const [events, setEvents] = useState([]);

	return (
		<div data-testid="testCalendar">
			<FullCalendar
				defaultView={defaultView}
				plugins={plugins}
				events={events}
			/>
		</div>
	);
};

export default Calendar;
