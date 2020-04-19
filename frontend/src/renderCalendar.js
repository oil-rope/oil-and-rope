import React, { Suspense } from "react";
import ReactDOM from "react-dom";
import Calendar from "./components/Calendar/Calendar";
import Loader from './components/loader/Loader';

let calendar = document.getElementById("oarCalendar");
if (calendar != null && calendar != undefined) {
	ReactDOM.render(
		<Suspense fallback={<Loader></Loader>}>
			<Calendar />
		</Suspense>, calendar);
}
