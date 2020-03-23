import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import BootstrapButton from './BootstrapButton';

class App extends Component {
    render() {
        return <h1 className="text-center">This is main page for testing react!</h1>
    }
}

ReactDOM.render(<App />, document.getElementById('reactApp'));

document.querySelectorAll('.bts-button').forEach(element => {
    ReactDOM.render(<BootstrapButton color="extra" />, element);
});
