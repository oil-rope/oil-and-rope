import React, { Suspense } from "react";
import ReactDOM from "react-dom";
import Loader from "./components/loader/Loader";

const Calendar = React.lazy(() => import("./components/calendar/Calendar"));

let calendar = document.getElementById("oarCalendar");
if (calendar != null && calendar != undefined) {
	const App = () => {
		return (
			<>
				<Suspense fallback={<Loader />}>
					<Calendar />
				</Suspense>
			</>
		);
	};
	ReactDOM.render(<App />, calendar);
}
