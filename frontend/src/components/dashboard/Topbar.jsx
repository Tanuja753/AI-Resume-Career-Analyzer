import { useAuth } from "../../context/AuthContext";

function Topbar() {
    const { user, logout } = useAuth();

    const initials =
        user?.full_name
            ?.split(" ")
            .map((name) => name.charAt(0))
            .slice(0, 2)
            .join("")
            .toUpperCase() || "U";

    return (
        <header className="topbar">

            <div className="topbar-left">

                <span className="topbar-breadcrumb">
                    Career Workspace
                </span>

                <span className="topbar-divider">
                    /
                </span>

                <strong>
                    Dashboard
                </strong>

            </div>


            <div className="topbar-right">

                <div className="topbar-profile">

                    <div className="topbar-user-text">

                        <strong>
                            {user?.full_name || "User"}
                        </strong>

                        <span>
                            {user?.email || ""}
                        </span>

                    </div>

                    <div className="topbar-avatar">
                        {initials}
                    </div>

                </div>


                <button
                    type="button"
                    className="topbar-logout"
                    onClick={logout}
                >
                    Logout
                </button>

            </div>

        </header>
    );
}

export default Topbar;