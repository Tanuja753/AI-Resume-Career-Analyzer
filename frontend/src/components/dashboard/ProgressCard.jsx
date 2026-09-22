function ProgressCard({
    percentage = 0,
    completed = 0,
    total = 0,
}) {
    const safePercentage = Math.min(
        100,
        Math.max(0, percentage)
    );

    return (
        <div className="progress-card">
            <div className="progress-header">
                <div>
                    <p className="card-eyebrow">
                        PREPARATION
                    </p>

                    <h3>Interview Preparation</h3>
                </div>

                <div className="progress-percentage">
                    {safePercentage.toFixed(0)}%
                </div>
            </div>

            <div className="progress-bar">
                <div
                    className="progress-bar-fill"
                    style={{
                        width: `${safePercentage}%`,
                    }}
                />
            </div>

            <div className="progress-footer">
                <span>
                    {completed} of {total} topics completed
                </span>

                <span>
                    Keep going
                </span>
            </div>
        </div>
    );
}

export default ProgressCard;