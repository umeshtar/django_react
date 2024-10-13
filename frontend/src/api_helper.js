import axios from "axios";
import Cookies from "js-cookie";

export const authFetch = axios.create({ baseURL: process.env.API_URL });

authFetch.interceptors.request.use(
    (request) => {
        const accessToken = (JSON.parse(Cookies.get("authUser") || null) || {})?.access
        if (accessToken) {
            request.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return request;
    },
    (error) => {
        return Promise.reject(error);
    }
);

authFetch.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const isLoginUrl = error.response.config.url.includes("token")
            if (isLoginUrl) {
                return Promise.reject(error)
            }
            const isTokenRefreshUrl = error.response.config.url.includes("token/refresh/")
            if (!isTokenRefreshUrl) {
                const authUser = JSON.parse(Cookies.get("authUser") || null)
                if (authUser.refresh) {
                    try {
                        const response = await authFetch.post("/token/refresh/", {
                            refresh: authUser.refresh,
                        });

                        const newAccessToken = response.data.access;
                        authUser.access = newAccessToken;
                        Cookies.set("authUser", JSON.stringify(authUser), { expires: 30 });

                        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
                        return authFetch(originalRequest);
                    } catch (refreshError) {
                        console.log("Error refreshing token:", refreshError);
                    }
                }

            } else {
                Cookies.remove("authUser");
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

