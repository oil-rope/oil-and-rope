import React from 'react';
import ReactDOM from 'react-dom';
import Calendar from '../Calendar';

it("Renders without problem", () => {
    const div = document.createElement('div');
    ReactDOM.render(<Calendar />, div);
});
