import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Home } from "../pages/Home/Home";
import { Login } from "../pages/login/Login";
import Cookies from "js-cookie";
import { PageNotFound } from "../components/PageNotFound";
import { employeeRoutes } from "./main/emp.routes";
import { Dashboard } from "../pages/Dashboard/Dashboard";

const authUser = Cookies.get("authUser")

const publicRoutes = [
    { path: "", element: authUser ? <Navigate to="/dashboard" /> : <Home /> },
    { path: "login", element: authUser ? <Navigate to="/dashboard" /> : <Login /> },
]

const protectedRoutes = [
    { path: "dashboard", element: <Dashboard /> },
    { path: "emp", element: <Outlet />, children: employeeRoutes },
]

export const router = createBrowserRouter([
    ...publicRoutes,
    { path: "", element: authUser ? <Outlet /> : <Navigate to="" />, children: protectedRoutes },
    { path: "*", element: <PageNotFound /> },
])





