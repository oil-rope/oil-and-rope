import React, { Component }  from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Container from 'react-bootstrap/Container'

class Chat extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: [],
      isLoading: true,
      placeholder: "Loading",
      open: false
    };
  }

  componentDidMount() {
    this.connector = new WebSocket('ws://localhost:8000/ws/chat/');
    this.connector.onopen = this.WSOnOpen;
    this.connector.onmessage = this.WSOnMessage;
    this.connector.onclose = this.WSOnClose;
  }

  WSOnOpen = () => {
    this.setState({
      open: true
    })
  }

  WSOnMessage = (message) => {

    console.log(message)
    this.setState({
      data: JSON.parse(message.data),
      isLoading: false,
      placeholder: "Loaded"
    })
  }

  WSOnClose = () => {
    this.setState({
      open: false
    })
  }

  handleJoin = (id) => {
    window.location.pathname = '/chat/' + id + '/';
  }

  handleCreate = () => {

   let element = $("#room-name-input").val();

   console.log(element)
   
   this.connector.send(JSON.stringify({
    'room_name': element
  }));

  }

  render() {

    if (this.state.isLoading== false) {
      
      return (
        <Container>
        
        <Row className="d-flex justify-content-center">
        {
          this.state.data['chats'].map((chat, i) => {
            return (
              
              <Card style={{ width: '18rem' }} className="d-flex" key={i}>
                  <Card.Title className="d-flex justify-content-center">Room {chat.name}</Card.Title>
                  <hr></hr>
                    <Card.Body>

                   {chat.users.map(function (user, i) {
                     return  <div key={i}>
                       <Card.Text>User {user} </Card.Text> 
                     </div>
                   })}
                   </Card.Body>
                  <Card.Footer className="d-flex justify-content-center">
                 <Button variant="primary" onClick={() => this.handleJoin(chat.id)}> Join</Button>
                  </Card.Footer>
                </Card>
 
            );
          })
        }
        </Row>
        <hr></hr>
        <Row className="d-flex justify-content-center">
          <Card style={{ width: '18rem' }} className="d-flex">
            <Card.Title className="d-flex justify-content-center"> Create a Room</Card.Title>
            <Card.Body>
            <Card.Text>
              Chat room name
            </Card.Text>
              <input id="room-name-input" type="text"></input>
            </Card.Body>
            <Card.Footer className="d-flex justify-content-center">
            <Button variant="primary" onClick={() => this.handleCreate()}> Create</Button>
            </Card.Footer>
          </Card>
        </Row>
        </Container>
     );


    } else {
      return(
        <ul>
        {this.state.placeholder}
        </ul>
      );
    }
  }

}

export default Chat;
