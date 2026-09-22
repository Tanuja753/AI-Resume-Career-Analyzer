import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import StatCard from "../components/dashboard/StatCard";
import ProgressCard from "../components/dashboard/ProgressCard";
import SectionCard from "../components/dashboard/SectionCard";

import {
    getResumeDrafts,
    getPreparationProgress,
    getCompatibility,
    getSkillGaps,
    getInterviewQuestionCount,
    getJobDescription,
} from "../services/dashboardService";

function Dashboard() {
    const { user } = useAuth();

    const [draftCount, setDraftCount] = useState(0);
    const [preparationProgress, setPreparationProgress] = useState(null);
    const [compatibility, setCompatibility] = useState(null);
    const [skillGaps, setSkillGaps] = useState(null);
    const [interviewQuestionCount, setInterviewQuestionCount] =
        useState(null);
    const [jobDescription, setJobDescription] = useState(null);

    const [loadingDrafts, setLoadingDrafts] = useState(true);
    const [loadingProgress, setLoadingProgress] = useState(true);
    const [loadingCompatibility, setLoadingCompatibility] = useState(true);
    const [loadingSkillGaps, setLoadingSkillGaps] = useState(true);
    const [loadingInterviewQuestions, setLoadingInterviewQuestions] =
        useState(true);
    const [loadingJobDescription, setLoadingJobDescription] = useState(true);

    const firstName = user?.full_name?.split(" ")[0] || "there";

    useEffect(() => {
        async function loadDashboardData() {
            const resumeId = localStorage.getItem("resume_id");
            const jobDescriptionId =
                localStorage.getItem("job_description_id");

            /* ---------------- Resume drafts ---------------- */

            try {
                const drafts = await getResumeDrafts();

                setDraftCount(
                    Array.isArray(drafts) ? drafts.length : 0
                );
            } catch (error) {
                console.error(
                    "Failed to load resume drafts:",
                    error
                );
                setDraftCount(0);
            } finally {
                setLoadingDrafts(false);
            }

            /* ---------------- Job description ---------------- */

            if (jobDescriptionId) {
                try {
                    const data = await getJobDescription(
                        Number(jobDescriptionId)
                    );

                    setJobDescription(data);
                } catch (error) {
                    console.error(
                        "Failed to load job description:",
                        error
                    );
                    setJobDescription(null);
                } finally {
                    setLoadingJobDescription(false);
                }
            } else {
                setLoadingJobDescription(false);
            }

            /* ---------------- Remaining analysis data ---------------- */

            if (!resumeId || !jobDescriptionId) {
                setLoadingInterviewQuestions(false);
                setLoadingSkillGaps(false);
                setLoadingProgress(false);
                setLoadingCompatibility(false);
                return;
            }

            const numericResumeId = Number(resumeId);
            const numericJobDescriptionId = Number(jobDescriptionId);

            /* Interview questions */

            getInterviewQuestionCount(
                numericResumeId,
                numericJobDescriptionId
            )
                .then((data) => {
                    setInterviewQuestionCount(data);
                })
                .catch((error) => {
                    console.error(
                        "Failed to load interview question count:",
                        error
                    );
                    setInterviewQuestionCount(null);
                })
                .finally(() => {
                    setLoadingInterviewQuestions(false);
                });

            /* Skill gaps */

            getSkillGaps(
                numericResumeId,
                numericJobDescriptionId
            )
                .then((data) => {
                    setSkillGaps(data);
                })
                .catch((error) => {
                    console.error(
                        "Failed to load skill gaps:",
                        error
                    );
                    setSkillGaps(null);
                })
                .finally(() => {
                    setLoadingSkillGaps(false);
                });

            /* Preparation progress */

            getPreparationProgress(
                numericResumeId,
                numericJobDescriptionId
            )
                .then((data) => {
                    setPreparationProgress(data);
                })
                .catch((error) => {
                    console.error(
                        "Failed to load preparation progress:",
                        error
                    );
                    setPreparationProgress(null);
                })
                .finally(() => {
                    setLoadingProgress(false);
                });

            /* Compatibility */

            getCompatibility(
                numericResumeId,
                numericJobDescriptionId
            )
                .then((data) => {
                    setCompatibility(data);
                })
                .catch((error) => {
                    console.error(
                        "Failed to load compatibility:",
                        error
                    );
                    setCompatibility(null);
                })
                .finally(() => {
                    setLoadingCompatibility(false);
                });
        }

        loadDashboardData();
    }, []);

    /* --------------------------------------------------
       Derived values
    -------------------------------------------------- */

    const compatibilityScore = compatibility
        ? Math.max(
              0,
              Math.min(
                  100,
                  Number(compatibility.compatibility_score) || 0
              )
          )
        : 0;

    const matchedSkills =
        skillGaps?.summary?.matched ?? 0;

    const totalRequiredSkills =
        skillGaps?.summary?.total_required ?? 0;

    const partialSkills =
        skillGaps?.summary?.partial ?? 0;

    const missingSkills =
        skillGaps?.summary?.missing ?? 0;

    const preparationPercentage =
        preparationProgress?.summary?.progress_percentage ?? 0;

    const completedTopics =
        preparationProgress?.summary?.completed ?? 0;

    const totalTopics =
        preparationProgress?.summary?.total_items ?? 0;

    const questionCount =
        interviewQuestionCount?.question_count ?? 0;

    return (
        <DashboardLayout>

            {/* =====================================================
                HERO
            ===================================================== */}

            <section className="dashboard-hero">

                <div className="dashboard-hero-content">

                    <span className="dashboard-eyebrow">
                        AI CAREER WORKSPACE
                    </span>

                    <h1>
                        Welcome back, {firstName}
                    </h1>

                    <p>
                        Your resume, skills, interview preparation,
                        and career progress — all in one place.
                    </p>

                </div>

                <div className="hero-status">
                    <span className="hero-status-dot" />
                    Profile active
                </div>

            </section>


            {/* =====================================================
                CAREER TARGET
            ===================================================== */}

            <section className="career-target-panel">

                <div className="career-target-left">

                    <span className="panel-label">
                        CURRENT CAREER TARGET
                    </span>

                    <h2>
                        {loadingJobDescription
                            ? "Loading target..."
                            : jobDescription?.target_job_title ||
                              "No target role selected"}
                    </h2>

                    <p>
                        Your dashboard is personalized around this
                        target role.
                    </p>

                </div>

                <Link
                    to="/job-description"
                    className="secondary-button"
                >
                    {jobDescription
                        ? "Change Target"
                        : "Set Target"}
                </Link>

            </section>


            {/* =====================================================
                QUICK STATS
            ===================================================== */}

            <section className="dashboard-stats">

                <StatCard
                    title="Compatibility"
                    value={
                        loadingCompatibility
                            ? "..."
                            : compatibility
                                ? `${Number(compatibilityScore).toFixed(2)}%`
                                : "—"
                    }
                    description="Resume-job match"
                    icon="◎"
                    variant="primary"
                />

                <StatCard
                    title="Skills Matched"
                    value={
                        loadingSkillGaps
                            ? "..."
                            : skillGaps
                                ? `${matchedSkills}/${totalRequiredSkills}`
                                : "—"
                    }
                    description="Required skills"
                    icon="◇"
                />

                <StatCard
                    title="Interview Questions"
                    value={
                        loadingInterviewQuestions
                            ? "..."
                            : interviewQuestionCount
                                ? questionCount
                                : "—"
                    }
                    description="Personalized for you"
                    icon="?"
                />

                <StatCard
                    title="Preparation"
                    value={
                        loadingProgress
                            ? "..."
                            : preparationProgress
                                ? `${preparationPercentage}%`
                                : "—"
                    }
                    description="Plan completed"
                    icon="↗"
                />

            </section>


            {/* =====================================================
                MAIN ANALYSIS AREA
            ===================================================== */}

            <section className="dashboard-main-grid">

                {/* -----------------------------------------------
                    Compatibility
                ----------------------------------------------- */}

                <SectionCard
                    title="Resume Compatibility"
                    subtitle="How well your resume matches the target role"
                    action={
                        <Link
                            to="/resume-analysis"
                            className="section-action"
                        >
                            View analysis →
                        </Link>
                    }
                >

                    <div className="compatibility-panel">

                        <div className="compatibility-score">

                            <div
                                className="compatibility-ring"
                                style={{
                                    "--score":
                                        `${compatibilityScore * 3.6}deg`,
                                }}
                            >
                                <div className="compatibility-ring-inner">
                                    <strong>
                                        {loadingCompatibility
                                            ? "..."
                                            : compatibility
                                                ? `${Number(compatibilityScore).toFixed(2)}%`
                                                : "—"}
                                    </strong>

                                    <span>
                                        Match
                                    </span>
                                </div>
                            </div>

                        </div>


                        <div className="compatibility-info">

                            <div className="analysis-status">
                                <span
                                    className={
                                        compatibility
                                            ? "status-indicator success"
                                            : "status-indicator"
                                    }
                                />

                                {compatibility
                                    ? "Analysis available"
                                    : "Analysis pending"}
                            </div>

                            <p>
                                {compatibility
                                    ? "Your resume has been analyzed against the selected job description."
                                    : "Run a resume analysis to calculate your compatibility."}
                            </p>

                            <div className="compatibility-metrics">

                                <div className="compatibility-metric">
                                    <strong>
                                        {compatibility?.matched ?? "—"}
                                    </strong>
                                    <span>Matched</span>
                                </div>

                                <div className="compatibility-metric">
                                    <strong>
                                        {compatibility?.partial ?? "—"}
                                    </strong>
                                    <span>Partial</span>
                                </div>

                                <div className="compatibility-metric">
                                    <strong>
                                        {compatibility?.missing ?? "—"}
                                    </strong>
                                    <span>Missing</span>
                                </div>

                            </div>

                        </div>

                    </div>

                </SectionCard>


                {/* -----------------------------------------------
                    Preparation
                ----------------------------------------------- */}

                <SectionCard
                    title="Preparation Progress"
                    subtitle="Your personalized interview preparation"
                    action={
                        <Link
                            to="/preparation-progress"
                            className="section-action"
                        >
                            View progress →
                        </Link>
                    }
                >

                    <ProgressCard
                        percentage={
                            loadingProgress
                                ? 0
                                : preparationPercentage
                        }
                        completed={
                            loadingProgress
                                ? 0
                                : completedTopics
                        }
                        total={
                            loadingProgress
                                ? 0
                                : totalTopics
                        }
                    />

                    <Link
                        to="/interview-preparation"
                        className="primary-action full-width"
                    >
                        Continue Preparation
                        <span>→</span>
                    </Link>

                </SectionCard>

            </section>


            {/* =====================================================
                SKILL OVERVIEW
            ===================================================== */}

            <SectionCard
                title="Skill Overview"
                subtitle="Skills identified from your resume and target job"
                action={
                    <Link
                        to="/skill-gaps"
                        className="section-action"
                    >
                        View skill gaps →
                    </Link>
                }
            >

                <div className="skill-overview">

                    {loadingSkillGaps ? (

                        <div className="dashboard-empty">
                            Loading skill analysis...
                        </div>

                    ) : !skillGaps ? (

                        <div className="dashboard-empty">
                            Analyze your resume against a job
                            description to see your skills.
                        </div>

                    ) : (

                        <>

                            <div className="skill-summary-grid">

                                <div className="skill-summary-card required">
                                    <strong>
                                        {totalRequiredSkills}
                                    </strong>
                                    <span>Required</span>
                                </div>

                                <div className="skill-summary-card matched">
                                    <strong>
                                        {matchedSkills}
                                    </strong>
                                    <span>Matched</span>
                                </div>

                                <div className="skill-summary-card partial">
                                    <strong>
                                        {partialSkills}
                                    </strong>
                                    <span>Partial</span>
                                </div>

                                <div className="skill-summary-card missing">
                                    <strong>
                                        {missingSkills}
                                    </strong>
                                    <span>Missing</span>
                                </div>

                            </div>


                            <div className="skill-section">

                                <div className="skill-section-header">
                                    <span className="skill-dot matched" />
                                    <span>Matched Skills</span>
                                </div>

                                <div className="skill-badges">

                                    {skillGaps.matched_skills?.length >
                                    0 ? (

                                        skillGaps.matched_skills.map(
                                            (skill) => (
                                                <span
                                                    key={skill.id}
                                                    className="skill-badge matched"
                                                    title={skill.reason}
                                                >
                                                    {skill.job_skill}
                                                </span>
                                            )
                                        )

                                    ) : (
                                        <span className="skill-empty">
                                            No matched skills
                                        </span>
                                    )}

                                </div>

                            </div>


                            {skillGaps.partial_skills?.length > 0 && (

                                <div className="skill-section">

                                    <div className="skill-section-header">
                                        <span className="skill-dot partial" />
                                        <span>Partial Skills</span>
                                    </div>

                                    <div className="skill-badges">

                                        {skillGaps.partial_skills.map(
                                            (skill) => (
                                                <span
                                                    key={skill.id}
                                                    className="skill-badge partial"
                                                    title={skill.reason}
                                                >
                                                    {skill.job_skill}
                                                </span>
                                            )
                                        )}

                                    </div>

                                </div>

                            )}


                            {skillGaps.missing_skills?.length > 0 && (

                                <div className="skill-section">

                                    <div className="skill-section-header">
                                        <span className="skill-dot missing" />
                                        <span>Missing Skills</span>
                                    </div>

                                    <div className="skill-badges">

                                        {skillGaps.missing_skills.map(
                                            (skill) => (
                                                <span
                                                    key={skill.id}
                                                    className="skill-badge missing"
                                                    title={skill.reason}
                                                >
                                                    {skill.job_skill}
                                                </span>
                                            )
                                        )}

                                    </div>

                                </div>

                            )}

                        </>

                    )}

                </div>

            </SectionCard>


            {/* =====================================================
                QUICK ACTIONS
            ===================================================== */}

            <section className="quick-actions">

                <div className="section-title-row">

                    <div>
                        <span className="panel-label">
                            NEXT STEPS
                        </span>

                        <h2>
                            Continue your career journey
                        </h2>

                        <p>
                            Pick up where you left off.
                        </p>
                    </div>

                </div>


                <div className="action-grid">

                    <Link
                        to="/resume-upload"
                        className="action-card"
                    >
                        <div className="action-card-icon">
                            ↑
                        </div>

                        <div className="action-card-content">
                            <h3>Upload Resume</h3>
                            <p>
                                Upload a new PDF or DOCX resume.
                            </p>
                        </div>

                        <span className="action-arrow">
                            →
                        </span>
                    </Link>


                    <Link
                        to="/job-description"
                        className="action-card"
                    >
                        <div className="action-card-icon">
                            +
                        </div>

                        <div className="action-card-content">
                            <h3>Add Job Description</h3>
                            <p>
                                Select the role you want to target.
                            </p>
                        </div>

                        <span className="action-arrow">
                            →
                        </span>
                    </Link>


                    <Link
                        to="/interview-preparation"
                        className="action-card"
                    >
                        <div className="action-card-icon">
                            ?
                        </div>

                        <div className="action-card-content">
                            <h3>Practice Interview</h3>
                            <p>
                                Practice personalized interview questions.
                            </p>
                        </div>

                        <span className="action-arrow">
                            →
                        </span>
                    </Link>


                    <Link
                        to="/resume-builder"
                        className="action-card"
                    >
                        <div className="action-card-icon">
                            ✎
                        </div>

                        <div className="action-card-content">
                            <h3>Build Resume</h3>
                            <p>
                                Create an ATS-friendly resume.
                            </p>
                        </div>

                        <span className="action-arrow">
                            →
                        </span>
                    </Link>

                </div>

            </section>

        </DashboardLayout>
    );
}

export default Dashboard;