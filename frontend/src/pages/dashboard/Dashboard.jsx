import { Link } from "react-router-dom";
import { handleLogout } from "../login/Login";

export function Dashboard() {
    return (
        <>
            <h1>Dashboard</h1>
            <div>
                <Link to='/emp/dept'> Department </Link>
            </div>
            <div>
                <button onClick={handleLogout}> Log Out </button>
            </div>
        </>
    )
}



