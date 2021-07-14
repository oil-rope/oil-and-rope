import Axios from "axios";

import * as Constants from "../../utils/constants.js";

/**
 * By current URL gets sessionID
 *
 * @returns Session ID
 */
const getSessionIDByPath = () => {
  const splitted_path = location.href.split("/");
  const split_length = splitted_path.length;
  const sessionID = splitted_path[split_length - 2];
  return sessionID;
};

/**
 * Calls API in order to lookup current Session.
 *
 * @returns {Promise} Response.
 */
export const getSession = () => {
  return Axios.get(`${Constants.SESSION_URL}/${getSessionIDByPath()}`)
    .then((res) => res)
    .catch(console.error);
};
