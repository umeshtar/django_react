import { Department } from "../../pages/main/Employee/Department";
import { Employee } from "../../pages/main/employee/Employee";

export const employeeRoutes = [
    { path: '', element: <Employee /> },
    { path: 'dept', element: <Department /> },
]


