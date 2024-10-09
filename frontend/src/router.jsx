import { createBrowserRouter } from "react-router-dom";
import { Employee } from "./pages/employee";
import { Department } from "./pages/designation";
import { Home } from "./pages/home";

export const router = createBrowserRouter([
    { path: '', element: <Home /> },
    { path: 'emp/', element: <Employee /> },
    { path: 'dept/', element: <Department /> },
])
