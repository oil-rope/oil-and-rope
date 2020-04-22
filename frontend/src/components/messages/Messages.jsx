import React, { Component }  from 'react';

class Messages extends Component {
  constructor(props) {
    super(props);

    this.state = {
      user: this.props.user,
      roomName: null,
      chatLog: [],
      isLoading: true,
      placeholder: "Loading",
      open: false
    };
  }

  componentDidMount() {
    //const roomName = JSON.parse(document.getElementById('room-name').textContent);
    
    const roomName = this.getRoomName();
    this.setRoomName(roomName);

    console.log(this.state.roomName);
    if(roomName){

      this.connector = new WebSocket('ws://localhost:8000/ws/chat/' + roomName + "/");
      this.connector.onopen = this.WSOnOpen;
      this.connector.onmessage = this.WSOnMessage;
      this.connector.onclose = this.WSOnClose;

    }else{
      console.error("Web socket not connected")
    }

    document.querySelector('#chat-message-input').focus();

    document.querySelector('#chat-message-input').onkeyup = function(e) {
      if (e.keyCode === 13) {  // enter, return
          document.querySelector('#chat-message-submit').click();
      }
  };

    document.querySelector('#chat-message-submit').onclick = this.WSSendMessage;

  
  }

  getRoomName = () => {

    let windowLocation = window.location.href;

    let indexes = [];
    for(let i = 0; i < windowLocation.length; i++) {
      if (windowLocation[i] === "/") indexes.push(i);
    }
    
    let roomName = windowLocation.substring(indexes[indexes.length-2]+1, indexes[indexes.length-1]);

    return roomName;
  }

  setRoomName = (room) => {
    this.setState({
      roomName: room
    })
  }

  WSOnOpen = () => {
    this.setState({
      open: true
    })
  }

  WSOnMessage = (message) => {
    const data = JSON.parse(message.data);

    document.querySelector('#chat-log').value += (data.message.user + ": " + data.message['message'] + '\n');

    this.setState({
        isLoading: false
    })
  }

  WSOnClose = () => {
    this.setState({
      open: false
    })
  }

  WSSendMessage = () => {

      const messageInputDom = document.querySelector('#chat-message-input');
      const message = messageInputDom.value;
      
      console.log(this.state.roomName)
      let d = new Date();
      d = d.toISOString();

      this.connector.send(JSON.stringify({
          'user': this.state.user,
          'chat': this.state.roomName,
          'message': message,
          'created_at': d
      }));
      messageInputDom.value = '';


  }

  render() {
    return null;
  }

}

export default Messages;
