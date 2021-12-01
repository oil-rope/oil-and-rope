/**
 * Look in cookies for Session Hash.
 *
 * @param {Function} callbackfn Function to call after session has is returned.
 */
export const getUserSessionFromCookies = (callbackfn) => {
	const cookies = document.cookie.split(";");
	cookies.forEach((cookie) => {
		const splittedCookie = cookie.split("=");
		const key = splittedCookie[0].trim();
		const value = splittedCookie[1].trim();
		if (key === "sessionid") {
			callbackfn(value);
		}
	});
};

export default getUserSessionFromCookies;
