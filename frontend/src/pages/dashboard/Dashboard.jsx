import { TitleComponent } from "../../components/CrudComponent";
import { Navigation } from "./Navigation";

export function Dashboard() {
    return (
        <>
            <TitleComponent {...{ title: "Dashboard" }} />
            <div className="container">
                <div className="sidebar">
                    <Navigation />
                </div>
                <div className="main-content">
                    <h2>Welcome to Dashboard</h2>
                </div>
            </div>
        </>
    )
}



