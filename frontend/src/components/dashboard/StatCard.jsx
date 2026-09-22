function StatCard({
    title,
    value,
    description,
    icon,
    className = "",
}) {
    return (
        <div className={`stat-card ${className}`}>
            <div className="stat-card-top">
                <div className="stat-icon">
                    {icon}
                </div>

                <span className="stat-label">
                    {title}
                </span>
            </div>

            <div className="stat-value">
                {value}
            </div>

            <div className="stat-description">
                {description}
            </div>
        </div>
    );
}

export default StatCard;