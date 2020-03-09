/**
 * Sets menu_referrer cookie to the actual value.
 *
 * @param e Menu PK.
 */
function setMenuReferrer(menuPK: number) {
    Cookies.set('_auth_user_menu_referrer', menuPK.toString());
}