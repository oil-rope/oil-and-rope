/**
 * Look in cookies for Session Hash.
 *
 * @param {Function} callbackfn Function to call after session has is returned.
 */
export const getUserSessionFromCookies = (callbackfn) => {
	const cookies = document.cookie.split(";");
	cookies.forEach((cookie) => {
		let splitted_cookie = cookie.split("=");
		let key = splitted_cookie[0].trim();
		let value = splitted_cookie[1].trim();
		if (key === "sessionid") {
			callbackfn(value);
		}
	});
};
