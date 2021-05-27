/**
 * Sets menu_referrer cookie to the actual value.
 *
 * @param {Number} menuPK Menu PK.
 */
function setMenuReferrer(menuPK) {
	Cookies.set("_auth_user_menu_referrer", menuPK.toString());
}

export default setMenuReferrer;
