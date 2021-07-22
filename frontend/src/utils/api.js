import Axios from "axios";

import * as Constants from "./constants";

/**
 * Checks if API is reachable.
 *
 * @returns {Promise} API active (true or false).
 */
export const checkAPIHealth = () =>
	Axios.get(`${Constants.API_URL}`)
		.then(
			(res) => res.status === 200 && parseFloat(res.data.drf_version) >= 3.12
		)
		.then((status) => status)
		.catch(console.error);

/**
 * Returns a URL resolved.
 *
 * @param {String} resolver The resolver for the URL.
 * @param {Object} extraParams Any extra arg to send POST.
 * @returns The URL resolved.
 */
export const resolveURL = (resolver, extraParams) =>
	Axios({
		method: "POST",
		url: `${Constants.RESOLVER_URL}`,
		data: {
			resolver,
			...extraParams,
		},
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
			"X-CSRFToken": Constants.CSRFToken,
		},
	})
		.then((res) => res.data)
		.then((data) => `${Constants.BASE_DOMAIN_URL}${data.url}`)
		.catch(console.error);
