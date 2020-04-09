import React from "react";
import ReactDOM from "react-dom";
import Calendar from "./components/calendar/Calendar";

let calendar = document.getElementById("oarCalendar");
if (calendar != null && calendar != undefined) {
	ReactDOM.render(<Calendar />, calendar);
}
