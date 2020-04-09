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
    fetch("api")
      .then(response => {
        if (response.status > 400) {
          return this.setState(() => {
            return { placeholder: "Something went wrong!" };
          });
        }
        return response.json();
      })
      .then(data => {
        this.setState(() => {
          return {
            data,
            loaded: true
          };
        });
      });
  }

  render() {
    if (this.state.data !== undefined) {

      console.log(this.state.data);
      const { data } = this.state.data;
      // return this.state.data.length ? this.renderData() : (
        // <span>Loading chats...</span>
        // )
      return this.renderData();
    }
  
  }


  renderData() {
    return (
      <ul>
        {console.log(this.state)}
        {

          this.state.data.forEach(element => {
            return (
              <li key={element.id}>
              {element.name}
            </li>
          );
        }) 
        }
      </ul>
    );
  }

}

export default Chat;
