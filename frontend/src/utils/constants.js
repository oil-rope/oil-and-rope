import Cookies from "js-cookie";

export const IS_SECURE = Boolean(location.protocol === "https:");
export const API_URL = `${location.protocol}//${process.env.API_URL}/api`;
export const RESOLVER_URL = `${API_URL}/resolver`;
export const USER_DETAIL = "api:registration:user-detail";
export const SESSION_URL = `${API_URL}/roleplay/session`;
export const WS_URL = process.env.WEBSOCKET_URL;
export const WS_CHAT = `${IS_SECURE ? "wss:" : "ws:"}//${WS_URL}/ws/chat/`;
export const CSRFToken = Cookies.get("csrftoken");
