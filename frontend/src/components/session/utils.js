import Axios from "axios";

import * as Constants from "../../utils/constants";
import { resolveURL } from "../../utils/api";

/**
 * By current URL gets sessionID
 *
 * @returns Session ID
 */
export const getSessionIDByPath = () => {
	const splittedPath = document.location.href.split("/");
	const splittedLength = splittedPath.length;
	const sessionID = splittedPath[splittedLength - 2];
	return sessionID;
};

/**
 * Calls API in order to lookup current Session.
 *
 * @returns {Promise} Response.
 */
export const getSession = () =>
	resolveURL(Constants.SESSION_DETAIL, { pk: getSessionIDByPath() }).then(
		(url) =>
			Axios.get(url)
				.then((res) => res)
				.catch(console.error)
	);
