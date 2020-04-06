import React from "react";
import ReactDOM from "react-dom";
import Calendar from "./components/Calendar/Calendar";

let calendar = document.getElementById("oarCalendar");
if (calendar != null && calendar != undefined) {
	ReactDOM.render(<Calendar />, calendar);
}
