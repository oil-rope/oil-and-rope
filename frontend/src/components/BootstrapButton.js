import React, { Component } from 'react'

export class BootstrapButton extends Component {

    constructor() {
        super();
    }

    render() {
        const {color} = this.props;
        return <a href="#" className={'btn btn-' + color}>Test button</a>;
    }
}

export default BootstrapButton;
