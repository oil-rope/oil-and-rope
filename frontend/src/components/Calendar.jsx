import React, { Component } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';

export class Calendar extends Component {
    render() {
        return (
            <FullCalendar defaultView="dayGridMonth" plugins={[ dayGridPlugin ]} />
        )
    }
}

export default Calendar;
