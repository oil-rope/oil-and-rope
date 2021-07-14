import * as Constants from "./constants.js";

/**
 * Checks if API is reachable.
 *
 * @returns {Promise} API active (true or false).
 */
export const checkAPIHealth = () => {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const initRequest = {
    method: "GET",
    headers: headers,
    mode: "cors",
  };
  const request = new Request(`${Constants.API_URL}/`, initRequest);
  return fetch(request)
    .then(
      (res) => res.status === 200 && parseFloat(res.json().drf_version) >= 3.12
    )
    .then((status) => status)
    .catch(console.error);
};

/**
 * Returns a URL resolved.
 *
 * @param {String} resolver The resolver for the URL.
 * @param {Object} extra_params Any extra arg to send POST.
 * @returns The URL resolved.
 */
export const resolveURL = ({ resolver, ...extra_params }) => {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const initRequest = {
    method: "POST",
    headers: headers,
    mode: "cors",
    body: JSON.stringify({ resolver, ...extra_params }),
  };
  const request = new Request(`${Constants.RESOLVER_URL}/`, { initRequest });
  return fetch(request)
    .then((res) => res.json())
    .then((data) => `${process.env.API_URL}${data.url}`)
    .catch(console.error);
};
