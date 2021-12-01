import Cookies from "js-cookie";

// Base
export const { API_DOMAIN } = process.env;
export const { WEBSOCKET_DOMAIN } = process.env;
export const BASE_DOMAIN_URL = `${document.location.protocol}//${API_DOMAIN}`;
export const BASE_WS_URL = `${
	document.location.protocol === "https:" ? "wss:" : "ws:"
}//${WEBSOCKET_DOMAIN}`;

// Base API
export const API_URL = `${BASE_DOMAIN_URL}/api`;
export const RESOLVER_URL = `${API_URL}/resolver/`;

// Resolvers
export const SESSION_DETAIL = "api:roleplay:session-detail";

export const WS_CHAT = `${BASE_WS_URL}/ws/chat/`;
export const CSRFToken = Cookies.get("csrftoken");
