import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Home } from "../pages/Home/Home";
import { Login } from "../pages/login/Login";
import Cookies from "js-cookie";
import { PageNotFound } from "../components/PageNotFound";
import { employeeRoutes } from "./main/emp.routes";
import { Dashboard } from "../pages/dashboard/Dashboard";
import { permissionRoutes } from "./main/permission.routes";
import { DynamicModule } from "../pages/dynamic/DynamicModule";

const authUser = Cookies.get("authUser")

const publicRoutes = [
    { path: "", element: authUser ? <Navigate to="/dashboard" /> : <Home /> },
    { path: "login", element: authUser ? <Navigate to="/dashboard" /> : <Login /> },
]

export const protectedRoutes = [
    { path: "dashboard", element: <Dashboard /> },
    { path: "emp/", element: <Outlet />, children: employeeRoutes },
    { path: "permission/", element: <Outlet />, children: permissionRoutes },
    { path: "dynamic/:id", element: <DynamicModule /> },
]

export const router = createBrowserRouter([
    ...publicRoutes,
    { path: "", element: authUser ? <Outlet /> : <Navigate to="" />, children: protectedRoutes },
    { path: "*", element: <PageNotFound /> },
])





