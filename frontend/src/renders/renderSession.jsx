import React from "react";
import ReactDOM from "react-dom";

import AuthContext from "../contexts/AuthContext.jsx";

import App from "../components/session/App.jsx";

const currentScript = document.currentScript;
let user = currentScript.getAttribute("data-user");
user = JSON.parse(user);

const RenderSession = () => {
  return (
    <AuthContext.Provider value={{ user }}>
      <App />
    </AuthContext.Provider>
  );
};

ReactDOM.render(<RenderSession />, document.getElementById("sessionDisplay"));
