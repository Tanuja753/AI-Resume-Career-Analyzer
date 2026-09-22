function SectionCard({
    title,
    subtitle,
    children,
    action,
}) {
    return (
        <section className="section-card">
            <div className="section-card-header">
                <div>
                    <h3>{title}</h3>

                    {subtitle && (
                        <p>{subtitle}</p>
                    )}
                </div>

                {action}
            </div>

            <div className="section-card-body">
                {children}
            </div>
        </section>
    );
}

export default SectionCard;