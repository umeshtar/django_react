import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Home } from "../pages/Home/Home";
import { Login, Logout } from "../pages/Login/Login";
import Cookies from "js-cookie";
import { PageNotFound } from "../components/PageNotFound";
import { employeeRoutes } from "./emp.routes";

const authUser = Cookies.get('authUser')

const publicRoutes = [
    { path: '', element: <Home /> },
    { path: 'login/', element: <Login /> },
]

const protectedRoutes = [
    { path: 'logout/', element: <Logout /> },
    { path: 'emp/', element: <Outlet />, children: employeeRoutes },
]

export const router = createBrowserRouter([
    ...publicRoutes,
    { path: '/', element: authUser ? <Outlet /> : <Navigate to="login/" />, children: protectedRoutes },
    { path: '*', element: <PageNotFound /> },
])





