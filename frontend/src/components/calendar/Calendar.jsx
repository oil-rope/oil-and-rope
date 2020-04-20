import React, { useState, Suspense } from "react";
import dayGridPlugin from "@fullcalendar/daygrid";
import Loader from "../loader/Loader";

const FullCalendar = React.lazy(() => import("@fullcalendar/react"));

const Calendar = () => {
	const [plugins, setPlugins] = useState([dayGridPlugin]);
	const [defaultView, setDefaultView] = useState("dayGridMonth");
	const [events, setEvents] = useState([]);

	return (
		<div data-testid="testCalendar">
			<Suspense fallback={<Loader/>}>
				<FullCalendar
					defaultView={defaultView}
					plugins={plugins}
					events={events}
				/>
			</Suspense>
		</div>
	);
};

export default Calendar;
