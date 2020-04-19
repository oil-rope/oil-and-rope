import React, { Component}  from 'react';
class Chat extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: [],
      loaded: false,
      placeholder: "Loading"
    };
  }

  componentDidMount() {
    console.log(this);
    this.connector = new WebSocket('ws://localhost:8000/chat/');
    this.connector.onmessage = this.WSOnMessage;
    this.connector.onerror = this.WSOnError;
    this.connector.onclose = this.WSOnClose;
    debugger;
  }

  WSOnMessage = (message) =>{
    let { exists, error } = JSON.parse(message.data);

    console.log(exists);
    console.log(error);

  }

  render() {

    return (
      <ul>
      </ul>
    );
  
  }

}

export default Chat;
