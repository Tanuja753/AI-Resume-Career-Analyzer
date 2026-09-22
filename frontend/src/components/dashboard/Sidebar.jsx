import { NavLink } from "react-router-dom";

const navigation = [
    {
        name: "Dashboard",
        path: "/dashboard",
        icon: "⌂",
    },
    {
        name: "Resume Analysis",
        path: "/resume-analysis",
        icon: "▣",
    },
    {
        name: "Skill Gaps",
        path: "/skill-gaps",
        icon: "◇",
    },
    {
        name: "Interview Preparation",
        path: "/interview-preparation",
        icon: "◈",
    },
    {
        name: "Preparation Progress",
        path: "/preparation-progress",
        icon: "↗",
    },
    {
        name: "Resume Builder",
        path: "/resume-builder",
        icon: "✎",
    },
];

function Sidebar() {
    return (
        <aside className="sidebar">

            {/* Brand */}

            <div className="sidebar-brand">

                <div className="brand-mark">
                    <span>AI</span>
                </div>

                <div className="brand-text">
                    <strong>ResumeAI</strong>
                    <span>Career Analyzer</span>
                </div>

            </div>


            {/* Navigation */}

            <nav className="sidebar-nav">

                <span className="sidebar-section-label">
                    WORKSPACE
                </span>

                <div className="sidebar-navigation">

                    {navigation.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `sidebar-link ${
                                    isActive ? "active" : ""
                                }`
                            }
                        >

                            <span className="sidebar-icon">
                                {item.icon}
                            </span>

                            <span className="sidebar-link-text">
                                {item.name}
                            </span>

                        </NavLink>
                    ))}

                </div>

            </nav>


            {/* Bottom */}

            <div className="sidebar-bottom">

                <div className="sidebar-tip">

                    <div className="sidebar-tip-icon">
                        ✦
                    </div>

                    <div>
                        <strong>
                            Career tip
                        </strong>

                        <span>
                            Keep your skills aligned with your target role.
                        </span>
                    </div>

                </div>

            </div>

        </aside>
    );
}

export default Sidebar;