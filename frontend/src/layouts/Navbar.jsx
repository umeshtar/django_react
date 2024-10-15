import { Link, useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

export function Navbar() {
    const navigate = useNavigate()

    const handleLogout = () => {
        Cookies.remove('authUser')
        navigate('/login')
    }

    return (
        <ul>
            <li><Link to='/'>Home</Link></li>
            <li><Link to='/emp'>Employee</Link></li>
            <li><Link to='/dept'>Department</Link></li>
            <li><button onClick={handleLogout}>Log out</button></li>
        </ul>
    )
}
