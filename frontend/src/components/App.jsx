import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import Calendar from './Calendar';

class App extends Component {
    render() {
        return <h1 className="text-center">This is main page for testing react!</h1>
    }
}

ReactDOM.render(<App />, document.getElementById('reactApp'));
ReactDOM.render(<Calendar /> , document.getElementById('oarCalendar'));
