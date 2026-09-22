import { useEffect, useState } from "react";
import api from "../api/axios";

function ResumeAnalysis() {
    const [jobDescription, setJobDescription] = useState(null);
    const [analysis, setAnalysis] = useState(null);

    const [loadingJob, setLoadingJob] = useState(true);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);

    const [error, setError] = useState("");

    const resumeId = localStorage.getItem("resume_id");
    const jobDescriptionId = localStorage.getItem(
        "job_description_id"
    );

    useEffect(() => {
        async function loadJobDescription() {
            if (!jobDescriptionId) {
                setError(
                    "Please process a job description before starting analysis."
                );
                setLoadingJob(false);
                return;
            }

            try {
                const response = await api.get(
                    `/job-descriptions/${jobDescriptionId}`
                );

                setJobDescription(response.data);
            } catch (err) {
                setError(
                    err.response?.data?.detail ||
                        "Failed to load job description."
                );
            } finally {
                setLoadingJob(false);
            }
        }

        loadJobDescription();
    }, [jobDescriptionId]);

    const handleAnalyze = async () => {
        setError("");

        if (!resumeId) {
            setError("Please upload a resume first.");
            return;
        }

        if (!jobDescriptionId) {
            setError("Please process a job description first.");
            return;
        }

        try {
            setLoadingAnalysis(true);

            // Step 1: Match resume skills with job skills
            await api.post(
                `/resumes/${resumeId}/match/${jobDescriptionId}`
            );

            // Step 2: Generate skill gap analysis
            const skillGapResponse = await api.post(
                `/skill-gaps/resume/${resumeId}/job-description/${jobDescriptionId}`
            );

            // Step 3: Calculate compatibility
            const compatibilityResponse = await api.post(
                `/job-compatibility/resume/${resumeId}/job-description/${jobDescriptionId}`
            );

            setAnalysis({
                skillGap: skillGapResponse.data,
                compatibility: compatibilityResponse.data,
            });
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                    "Failed to analyze resume."
            );
        } finally {
            setLoadingAnalysis(false);
        }
    };

    if (loadingJob) {
        return (
            <div className="resume-analysis-page">
                <div className="resume-analysis-loading">
                    Loading job description...
                </div>
            </div>
        );
    }

    const compatibility = analysis?.compatibility;
    const skillGap = analysis?.skillGap;
    const summary = skillGap?.summary;

    const compatibilityScore =
        compatibility?.compatibility_score ?? 0;

    return (
        <div className="resume-analysis-page">

            {/* PAGE HEADER */}
            <div className="resume-analysis-header">
                <div>
                    <p className="resume-analysis-eyebrow">
                        RESUME COMPATIBILITY
                    </p>

                    <h1>Resume Analysis</h1>

                    <p className="resume-analysis-subtitle">
                        Understand how well your resume matches your
                        selected target role.
                    </p>
                </div>

                {analysis && (
                    <div className="resume-analysis-header-score">
                        <span>Compatibility</span>
                        <strong>{Number(compatibilityScore).toFixed(2)}%</strong>
                    </div>
                )}
            </div>

            {/* ERROR */}
            {error && (
                <div className="resume-analysis-error">
                    <strong>Analysis error</strong>
                    <span>{error}</span>
                </div>
            )}

            {/* TARGET JOB */}
            {jobDescription && (
                <section className="resume-analysis-role-card">

                    <div>
                        <span className="resume-analysis-role-label">
                            TARGET ROLE
                        </span>

                        <h2>
                            {jobDescription.target_job_title}
                        </h2>

                        <p>
                            Your resume will be evaluated against
                            the requirements of this role.
                        </p>
                    </div>

                    <div className="resume-analysis-role-icon">
                        ↗
                    </div>
                </section>
            )}

            {/* ANALYZE BUTTON */}
            {!analysis && (
                <section className="resume-analysis-start-card">

                    <div>
                        <span className="resume-analysis-start-icon">
                            ✦
                        </span>

                        <div>
                            <h2>
                                Ready to analyze your resume?
                            </h2>

                            <p>
                                We will compare your resume skills
                                with the selected job requirements
                                and calculate your compatibility.
                            </p>
                        </div>
                    </div>

                    <button
                        className="resume-analysis-button"
                        onClick={handleAnalyze}
                        disabled={loadingAnalysis}
                    >
                        {loadingAnalysis
                            ? "Analyzing Resume..."
                            : "Analyze Resume"}
                    </button>

                </section>
            )}

            {/* RESULTS */}
            {analysis && (
                <>
                    {/* COMPATIBILITY OVERVIEW */}
                    <section className="resume-analysis-card">

                        <div className="resume-analysis-card-header">
                            <div>
                                <h2>
                                    Compatibility Overview
                                </h2>

                                <p>
                                    Overall alignment between your
                                    resume and the target job.
                                </p>
                            </div>

                            <span className="analysis-status-badge">
                                Analysis Complete
                            </span>
                        </div>

                        <div className="compatibility-analysis-grid">

                            {/* SCORE */}
                            <div className="compatibility-score-panel">

                                <div
                                    className="compatibility-score-ring"
                                    style={{
                                        "--score":
                                            `${compatibilityScore * 3.6}deg`,
                                    }}
                                >
                                    <div>
                                        <strong>
                                            {Number(compatibilityScore).toFixed(2)}
                                        </strong>
                                        <span>%</span>
                                    </div>
                                </div>

                                <h3>
                                    Resume Compatibility
                                </h3>

                                <p>
                                    Based on skill coverage and
                                    semantic skill matching.
                                </p>
                            </div>

                            {/* METRICS */}
                            <div className="compatibility-metrics">

                                <div className="compatibility-metric">
                                    <span>
                                        Skill Coverage
                                    </span>

                                    <strong>
                                        {Number(
                                            compatibility.skill_coverage_percentage
                                        ).toFixed(2)}%
                                    </strong>

                                    <div className="metric-bar">
                                        <div
                                            style={{
                                                width: `${compatibility.skill_coverage_percentage}%`,
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="compatibility-metric">
                                    <span>
                                        Semantic Match
                                    </span>

                                    <strong>
                                        {Number(
                                            compatibility.semantic_match_percentage
                                        ).toFixed(2)}%
                                    </strong>

                                    <div className="metric-bar">
                                        <div
                                            style={{
                                                width: `${compatibility.semantic_match_percentage}%`,
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="compatibility-explanation">
                                    <span>
                                        HOW THIS SCORE WAS CALCULATED
                                    </span>

                                    <p>
                                        {compatibility.explanation}
                                    </p>
                                </div>

                            </div>
                        </div>
                    </section>

                    {/* SKILL SUMMARY */}
                    <section className="resume-analysis-card">

                        <div className="resume-analysis-card-header">
                            <div>
                                <h2>
                                    Skill Match Summary
                                </h2>

                                <p>
                                    Breakdown of the skills required
                                    by the target role.
                                </p>
                            </div>
                        </div>

                        <div className="analysis-summary-grid">

                            <div className="analysis-summary-item">
                                <span>
                                    Required Skills
                                </span>

                                <strong>
                                    {summary.total_required}
                                </strong>
                            </div>

                            <div className="analysis-summary-item analysis-summary-matched">
                                <span>
                                    Matched
                                </span>

                                <strong>
                                    {summary.matched}
                                </strong>
                            </div>

                            <div className="analysis-summary-item analysis-summary-partial">
                                <span>
                                    Partial
                                </span>

                                <strong>
                                    {summary.partial}
                                </strong>
                            </div>

                            <div className="analysis-summary-item analysis-summary-missing">
                                <span>
                                    Missing
                                </span>

                                <strong>
                                    {summary.missing}
                                </strong>
                            </div>

                        </div>
                    </section>

                    {/* MATCHED SKILLS */}
                    <section className="resume-analysis-card">

                        <div className="resume-analysis-card-header">
                            <div>
                                <h2>
                                    Matched Skills
                                </h2>

                                <p>
                                    Skills from the job description
                                    that are supported by your resume.
                                </p>
                            </div>

                            <span className="analysis-count-badge matched">
                                {summary.matched} matched
                            </span>
                        </div>

                        {skillGap.matched_skills.length === 0 ? (
                            <div className="analysis-empty-state">
                                No matched skills found.
                            </div>
                        ) : (
                            <div className="analysis-skill-list">
                                {skillGap.matched_skills.map(
                                    (skill) => (
                                        <div
                                            className="analysis-skill-card matched"
                                            key={skill.id}
                                        >
                                            <div className="analysis-skill-icon">
                                                ✓
                                            </div>

                                            <div className="analysis-skill-content">
                                                <strong>
                                                    {skill.job_skill}
                                                </strong>

                                                <span>
                                                    Resume skill:{" "}
                                                    {skill.resume_skill ||
                                                        "Not identified"}
                                                </span>
                                            </div>

                                            <div className="analysis-skill-match">
                                                {skill.similarity_score !==
                                                null
                                                    ? `${Math.round(
                                                          skill.similarity_score *
                                                              100
                                                      )}%`
                                                    : "Direct"}
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>
                        )}
                    </section>

                    {/* PARTIAL SKILLS */}
                    <section className="resume-analysis-card">

                        <div className="resume-analysis-card-header">
                            <div>
                                <h2>
                                    Partial Matches
                                </h2>

                                <p>
                                    Related skills that may require
                                    additional preparation.
                                </p>
                            </div>

                            <span className="analysis-count-badge partial">
                                {summary.partial} partial
                            </span>
                        </div>

                        {skillGap.partial_skills.length === 0 ? (
                            <div className="analysis-empty-state success">
                                No partial skill gaps detected.
                            </div>
                        ) : (
                            <div className="analysis-skill-list">
                                {skillGap.partial_skills.map(
                                    (skill) => (
                                        <div
                                            className="analysis-skill-card partial"
                                            key={skill.id}
                                        >
                                            <div className="analysis-skill-icon">
                                                ~
                                            </div>

                                            <div className="analysis-skill-content">
                                                <strong>
                                                    {skill.job_skill}
                                                </strong>

                                                <span>
                                                    Resume skill:{" "}
                                                    {skill.resume_skill ||
                                                        "Not identified"}
                                                </span>
                                            </div>

                                            <div className="analysis-skill-match">
                                                {skill.similarity_score !==
                                                null
                                                    ? `${Math.round(
                                                          skill.similarity_score *
                                                              100
                                                      )}%`
                                                    : "Partial"}
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>
                        )}
                    </section>

                    {/* MISSING SKILLS */}
                    <section className="resume-analysis-card">

                        <div className="resume-analysis-card-header">
                            <div>
                                <h2>
                                    Missing Skills
                                </h2>

                                <p>
                                    Required skills that were not
                                    identified in your resume.
                                </p>
                            </div>

                            <span className="analysis-count-badge missing">
                                {summary.missing} missing
                            </span>
                        </div>

                        {skillGap.missing_skills.length === 0 ? (
                            <div className="analysis-empty-state success">
                                <strong>
                                    No missing skills detected.
                                </strong>

                                <span>
                                    All currently processed job
                                    requirements are represented in
                                    your resume.
                                </span>
                            </div>
                        ) : (
                            <div className="analysis-skill-list">
                                {skillGap.missing_skills.map(
                                    (skill) => (
                                        <div
                                            className="analysis-skill-card missing"
                                            key={skill.id}
                                        >
                                            <div className="analysis-skill-icon">
                                                !
                                            </div>

                                            <div className="analysis-skill-content">
                                                <strong>
                                                    {skill.job_skill}
                                                </strong>

                                                <span>
                                                    Required by target
                                                    role
                                                </span>
                                            </div>

                                            <div className="analysis-skill-match">
                                                Missing
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>
                        )}
                    </section>
                </>
            )}
        </div>
    );
}

export default ResumeAnalysis;