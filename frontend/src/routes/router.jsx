import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Home } from "../pages/Home/Home";
import { Login } from "../pages/Login/Login";
import Cookies from "js-cookie";
import { PageNotFound } from "../components/PageNotFound";
import { employeeRoutes } from "./emp.routes";
import { designationRoutes } from "./designation.routes";

const authUser = Cookies.get('authUser')

const publicRoutes = [
    { path: '', element: <Home /> },
]

const nonAuthRoutes = [
    { path: 'login/', element: <Login /> },
]

const authRoutes = [
    { path: 'emp/', element: <Outlet />, children: employeeRoutes },
    { path: 'dept/', element: <Outlet />, children: designationRoutes },
]

export const router = createBrowserRouter([
    ...publicRoutes,
    ...nonAuthRoutes,
    { path: '/', element: authUser ? <Outlet /> : <Navigate to="login/" />, children: authRoutes },
    { path: '*', element: <PageNotFound /> },
])





