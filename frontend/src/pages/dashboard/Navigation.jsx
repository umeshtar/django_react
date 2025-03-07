import { Link } from "react-router-dom";

export function Navigation() {

    return <ul>
        <li>
            <Link to="/dashboard">Dashboard</Link>
        </li>

        <li>Employee
            <ul>
                <li>
                    <Link to="/emp/dept">Department</Link>
                </li>
                <li>
                    <Link to="/emp">Employee</Link>
                </li>
            </ul>
        </li>
        <li>Permission
            <ul>
                <li>
                    <Link to="/permission/module_configuration">Module Configuration</Link>
                </li>
            </ul>
        </li>
    </ul>
}

