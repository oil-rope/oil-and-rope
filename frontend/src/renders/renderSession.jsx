import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import App from "../components/session/App.jsx";
import SessionContext from "../contexts/SessionContext.jsx";
import AuthContext from "../contexts/AuthContext.jsx";

import * as Constants from "../utils/constants.js";

const currentScript = document.currentScript;
let user = currentScript.getAttribute("data-user");
user = JSON.parse(user);

const RenderSession = () => {
  const [sessionID, setSessionID] = useState(null);
  const [session, setSession] = useState(null);

  const getSessionIDByPath = () => {
    const splitted_path = location.href.split("/");
    const split_length = splitted_path.length;
    const sessionID = splitted_path[split_length - 2];
    setSessionID(sessionID);
    return sessionID;
  };

  const getSession = () => {
    if (sessionID !== null) {
      // Setting up headers
      const headers = new Headers();
      headers.append("Content-Type", "application/json");
      headers.append("Accept", "application/json");
      // Setting up request
      const initRequest = {
        method: "GET",
        headers: headers,
        mode: "cors",
      };
      const request = new Request(
        `${Constants.SESSION_URL}/${sessionID}/`,
        initRequest
      );
      fetch(request)
        .then((res) => res.json())
        .then(setSession);
    }
  };

  useEffect(() => {
    getSessionIDByPath();
  }, []);

  useEffect(() => {
    getSession();
  }, [sessionID]);

  return (
    <AuthContext.Provider value={{ user, userToken: user.auth_token }}>
      <SessionContext.Provider value={{ session }}>
        <App />
      </SessionContext.Provider>
    </AuthContext.Provider>
  );
};

ReactDOM.render(<RenderSession />, document.getElementById("sessionDisplay"));
