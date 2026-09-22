import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

function DashboardLayout({ children }) {
    return (
        <div className="dashboard-shell">

            <Sidebar />

            <div className="dashboard-main">

                <Topbar />

                <main className="dashboard-content">
                    {children}
                </main>

            </div>

        </div>
    );
}

export default DashboardLayout;