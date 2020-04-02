import React, { Component } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';

import './main.scss';

export class Calendar extends Component {
    render() {
        return (
            <FullCalendar data-testid="calendar" defaultView="dayGridMonth" plugins={[ dayGridPlugin ]} />
        )
    }
}

export default Calendar;
