import React from "react";
import ReactDOM from "react-dom";

import AuthContext from "../contexts/AuthContext.jsx";

import App from "../components/session/App.jsx";

const currentScript = document.currentScript;
const plainUser = currentScript.getAttribute("data-user");

const RenderSession = () => {
  const user = JSON.parse(plainUser);

  return (
    <AuthContext.Provider value={{ user }}>
      <App />
    </AuthContext.Provider>
  );
};

ReactDOM.render(<RenderSession />, document.getElementById("sessionDisplay"));
