import { Link } from "react-router-dom";

export function Navbar() {
    return (
        <ul>
            <li><Link to='/'>Home</Link></li>
            <li><Link to='/emp'>Employee</Link></li>
            <li><Link to='/dept'>Department</Link></li>
            <li><Link to='/login'>Log out</Link></li>
        </ul>
    )
}
