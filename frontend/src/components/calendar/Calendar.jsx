import React, { Component } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';

import './main.scss';

export class Calendar extends Component {
    render() {
        return (
            <div data-testid="calendar">
                <FullCalendar defaultView="dayGridMonth" plugins={[ dayGridPlugin ]} />
            </div>
        )
    }
}

export default Calendar;
