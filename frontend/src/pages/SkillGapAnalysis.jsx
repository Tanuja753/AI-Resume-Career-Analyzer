import { useEffect, useState } from "react";

import SectionCard from "../components/dashboard/SectionCard";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";

import {
    getSkillGaps,
    getJobDescription,
} from "../services/dashboardService";

function SkillGapAnalysis() {
    const [skillGaps, setSkillGaps] = useState(null);
    const [jobDescription, setJobDescription] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    async function loadSkillGaps() {
        try {
            setLoading(true);
            setError("");

            const resumeId =
                localStorage.getItem("resume_id");

            const jobDescriptionId =
                localStorage.getItem("job_description_id");

            if (!resumeId || !jobDescriptionId) {
                setError(
                    "Resume or job description information is missing."
                );
                return;
            }

            const [gapData, jobData] = await Promise.all([
                getSkillGaps(
                    resumeId,
                    jobDescriptionId
                ),
                getJobDescription(jobDescriptionId),
            ]);

            setSkillGaps(gapData);
            setJobDescription(jobData);
        } catch (err) {
            console.error(
                "Failed to load skill gap analysis:",
                err
            );

            setError(
                err.response?.data?.detail ||
                    "Failed to load skill gap analysis."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadSkillGaps();
    }, []);

    const matchedSkills =
        skillGaps?.matched_skills || [];

    const partialSkills =
        skillGaps?.partial_skills || [];

    const missingSkills =
        skillGaps?.missing_skills || [];

    const totalRequired =
        skillGaps?.summary?.total_required ?? 0;

    function getSkillName(skillGap) {
        if (typeof skillGap === "string") {
            return skillGap;
        }

        return (
            skillGap?.job_skill ||
            skillGap?.resume_skill ||
            "Unknown skill"
        );
    }

    function getResumeSkill(skillGap) {
        if (typeof skillGap === "string") {
            return skillGap;
        }

        return skillGap?.resume_skill || "Not identified";
    }

    function getSimilarity(skillGap) {
        if (
            typeof skillGap !== "object" ||
            skillGap?.similarity_score === null ||
            skillGap?.similarity_score === undefined
        ) {
            return null;
        }

        return Math.round(
            Number(skillGap.similarity_score) * 100
        );
    }

    function SkillMatchCard({
        skillGap,
        type,
    }) {
        const skillName = getSkillName(skillGap);
        const resumeSkill = getResumeSkill(skillGap);
        const similarity = getSimilarity(skillGap);

        const isMatched = type === "matched";
        const isPartial = type === "partial";

        return (
            <div
                className={`skill-detail-card skill-detail-${type}`}
            >
                <div className="skill-detail-top">
                    <div className="skill-detail-name">
                        <div className="skill-detail-icon">
                            {isMatched
                                ? "✓"
                                : isPartial
                                  ? "~"
                                  : "!"}
                        </div>

                        <div>
                            <strong>
                                {skillName}
                            </strong>

                            <span>
                                Required skill
                            </span>
                        </div>
                    </div>

                    {similarity !== null && (
                        <div className="skill-similarity">
                            <strong>
                                {similarity}%
                            </strong>

                            <span>
                                similarity
                            </span>
                        </div>
                    )}
                </div>

                <div className="skill-detail-info">
                    <div>
                        <span>
                            RESUME SKILL
                        </span>

                        <strong>
                            {resumeSkill}
                        </strong>
                    </div>

                    <div>
                        <span>
                            MATCH TYPE
                        </span>

                        <strong>
                            {isMatched
                                ? "Direct match"
                                : isPartial
                                  ? "Related match"
                                  : "Missing"}
                        </strong>
                    </div>
                </div>

                {skillGap?.reason && (
                    <div className="skill-detail-reason">
                        <span>
                            AI ANALYSIS
                        </span>

                        <p>
                            {skillGap.reason}
                        </p>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="skill-gap-page">
            <div className="skill-gap-header">
                <div>
                    <div className="skill-gap-eyebrow">
                        SKILL ANALYSIS
                    </div>

                    <h1>
                        Skill Gap Analysis
                    </h1>

                    <p>
                        Understand how your current
                        skills align with your target
                        role.
                    </p>
                </div>

                {skillGaps && (
                    <div className="skill-gap-header-stat">
                        <span>
                            Skills identified
                        </span>

                        <strong>
                            {totalRequired}
                        </strong>
                    </div>
                )}
            </div>

            {loading && <Loading />}

            {!loading && error && (
                <ErrorMessage message={error} />
            )}

            {!loading &&
                !error &&
                skillGaps && (
                    <>
                        {/* Target Role */}

                        <div className="skill-gap-role-card">
                            <div>
                                <span>
                                    TARGET ROLE
                                </span>

                                <h2>
                                    {jobDescription?.target_job_title ||
                                        "Target role"}
                                </h2>

                                <p>
                                    Required skills compared
                                    with the skills identified
                                    in your resume.
                                </p>
                            </div>

                            <div className="skill-gap-role-icon">
                                ✦
                            </div>
                        </div>

                        {/* Summary */}

                        <div className="skill-gap-stat-grid">
                            <div className="skill-gap-stat-card">
                                <span>
                                    Required
                                </span>

                                <strong>
                                    {totalRequired}
                                </strong>

                                <small>
                                    Skills in job description
                                </small>
                            </div>

                            <div className="skill-gap-stat-card skill-gap-stat-matched">
                                <span>
                                    Matched
                                </span>

                                <strong>
                                    {matchedSkills.length}
                                </strong>

                                <small>
                                    Directly identified
                                </small>
                            </div>

                            <div className="skill-gap-stat-card skill-gap-stat-partial">
                                <span>
                                    Partial
                                </span>

                                <strong>
                                    {partialSkills.length}
                                </strong>

                                <small>
                                    Related or incomplete
                                </small>
                            </div>

                            <div className="skill-gap-stat-card skill-gap-stat-missing">
                                <span>
                                    Missing
                                </span>

                                <strong>
                                    {missingSkills.length}
                                </strong>

                                <small>
                                    Not identified
                                </small>
                            </div>
                        </div>

                        {/* Matched Skills */}

                        <SectionCard
                            title="Matched Skills"
                            subtitle="Skills directly aligned with the target role"
                        >
                            {matchedSkills.length > 0 ? (
                                <div className="skill-detail-list">
                                    {matchedSkills.map(
                                        (skillGap) => (
                                            <SkillMatchCard
                                                key={
                                                    skillGap.id ??
                                                    getSkillName(
                                                        skillGap
                                                    )
                                                }
                                                skillGap={
                                                    skillGap
                                                }
                                                type="matched"
                                            />
                                        )
                                    )}
                                </div>
                            ) : (
                                <div className="skill-empty-state">
                                    No matched skills found.
                                </div>
                            )}
                        </SectionCard>

                        {/* Partial Skills */}

                        {partialSkills.length > 0 && (
                            <SectionCard
                                title="Partial / Related Skills"
                                subtitle="Skills that have some relationship but may require stronger alignment"
                            >
                                <div className="skill-detail-list">
                                    {partialSkills.map(
                                        (skillGap) => (
                                            <SkillMatchCard
                                                key={
                                                    skillGap.id ??
                                                    getSkillName(
                                                        skillGap
                                                    )
                                                }
                                                skillGap={
                                                    skillGap
                                                }
                                                type="partial"
                                            />
                                        )
                                    )}
                                </div>
                            </SectionCard>
                        )}

                        {/* Missing Skills */}

                        {missingSkills.length > 0 && (
                            <SectionCard
                                title="Missing Skills"
                                subtitle="Required skills not identified in your resume"
                            >
                                <div className="skill-detail-list">
                                    {missingSkills.map(
                                        (skillGap) => (
                                            <SkillMatchCard
                                                key={
                                                    skillGap.id ??
                                                    getSkillName(
                                                        skillGap
                                                    )
                                                }
                                                skillGap={
                                                    skillGap
                                                }
                                                type="missing"
                                            />
                                        )
                                    )}
                                </div>
                            </SectionCard>
                        )}

                        {/* Complete Coverage */}

                        {partialSkills.length === 0 &&
                            missingSkills.length === 0 && (
                                <div className="skill-complete-banner">
                                    <div className="skill-complete-icon">
                                        ✓
                                    </div>

                                    <div>
                                        <strong>
                                            All identified
                                            skills are covered
                                        </strong>

                                        <p>
                                            Your resume contains
                                            all required skills
                                            identified from this
                                            job description.
                                        </p>
                                    </div>
                                </div>
                            )}
                    </>
                )}
        </div>
    );
}

export default SkillGapAnalysis;