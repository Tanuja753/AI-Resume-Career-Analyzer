import { useEffect, useState } from "react";

import SectionCard from "../components/dashboard/SectionCard";
import ProgressCard from "../components/dashboard/ProgressCard";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";

import {
    getPreparationPlan,
    generatePreparationPlan,
    getPreparationProgress,
    updatePreparationProgress,
} from "../services/dashboardService";

function PreparationProgress() {
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updatingItem, setUpdatingItem] = useState(null);

    async function loadProgress() {
        try {
            setLoading(true);
            setError("");

            const resumeId = localStorage.getItem("resume_id");

            const jobDescriptionId =
                localStorage.getItem("job_description_id");

            if (!resumeId || !jobDescriptionId) {
                setError(
                    "Resume or job description information is missing."
                );
                return;
            }

            // ---------------------------------------------------------
            // Step 1: Check whether a preparation plan already exists
            // ---------------------------------------------------------

            try {
                await getPreparationPlan(
                    resumeId,
                    jobDescriptionId
                );
            } catch (err) {
                // -----------------------------------------------------
                // If plan does not exist, generate it once
                // -----------------------------------------------------

                if (err.response?.status === 404) {
                    await generatePreparationPlan(
                        resumeId,
                        jobDescriptionId
                    );
                } else {
                    throw err;
                }
            }

            // ---------------------------------------------------------
            // Step 2: Load preparation progress
            // ---------------------------------------------------------

            const data = await getPreparationProgress(
                resumeId,
                jobDescriptionId
            );

            setProgress(data);
        } catch (err) {
            console.error(
                "Failed to load preparation progress:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to load preparation progress."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadProgress();
    }, []);

    async function handleStatusChange(planItemId, newStatus) {
        try {
            setUpdatingItem(planItemId);
            setError("");

            await updatePreparationProgress(
                planItemId,
                newStatus
            );

            await loadProgress();
        } catch (err) {
            console.error(
                "Failed to update preparation progress:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to update preparation progress."
            );
        } finally {
            setUpdatingItem(null);
        }
    }

    function getPriorityClass(priority) {
        if (priority === "high") {
            return "prep-priority prep-priority-high";
        }

        if (priority === "medium") {
            return "prep-priority prep-priority-medium";
        }

        return "prep-priority prep-priority-low";
    }

    function getStatusClass(status) {
        if (status === "completed") {
            return "prep-status prep-status-completed";
        }

        if (status === "in_progress") {
            return "prep-status prep-status-progress";
        }

        return "prep-status prep-status-not-started";
    }

    function getStatusLabel(status) {
        if (status === "in_progress") {
            return "In Progress";
        }

        if (status === "completed") {
            return "Completed";
        }

        return "Not Started";
    }

    return (
        <div className="preparation-page">
            <div className="preparation-page-header">
                <div>
                    <div className="preparation-eyebrow">
                        INTERVIEW PREPARATION
                    </div>

                    <h1>Preparation Progress</h1>

                    <p>
                        Track your preparation journey and build
                        confidence for your target role.
                    </p>
                </div>

                {progress && (
                    <div className="preparation-header-stat">
                        <span>Overall progress</span>

                        <strong>
                            {Math.round(
                                progress.summary?.progress_percentage ?? 0
                            )}
                            %
                        </strong>
                    </div>
                )}
            </div>

            {loading && <Loading />}

            {!loading && error && (
                <ErrorMessage message={error} />
            )}

            {!loading && !error && progress && (
                <>
                    <SectionCard title="Your Progress">
                        <div className="preparation-progress-card">
                            <ProgressCard
                                percentage={
                                    progress.summary
                                        ?.progress_percentage ?? 0
                                }
                                completed={
                                    progress.summary?.completed ?? 0
                                }
                                total={
                                    progress.summary?.total_items ?? 0
                                }
                            />

                            <div className="preparation-stat-grid">
                                <div className="preparation-mini-stat">
                                    <span>Total Topics</span>
                                    <strong>
                                        {progress.summary?.total_items ??
                                            0}
                                    </strong>
                                </div>

                                <div className="preparation-mini-stat">
                                    <span>Completed</span>
                                    <strong>
                                        {progress.summary?.completed ??
                                            0}
                                    </strong>
                                </div>

                                <div className="preparation-mini-stat">
                                    <span>In Progress</span>
                                    <strong>
                                        {progress.summary?.in_progress ??
                                            0}
                                    </strong>
                                </div>

                                <div className="preparation-mini-stat">
                                    <span>Not Started</span>
                                    <strong>
                                        {progress.summary?.not_started ??
                                            0}
                                    </strong>
                                </div>
                            </div>
                        </div>
                    </SectionCard>

                    <div className="preparation-section-heading">
                        <div>
                            <h2>Interview Preparation</h2>
                            <p>
                                Work through each topic and update your
                                status as you progress.
                            </p>
                        </div>

                        <div className="preparation-topic-count">
                            {progress.summary?.completed ?? 0}/
                            {progress.summary?.total_items ?? 0} completed
                        </div>
                    </div>

                    <div className="preparation-topic-list">
                        {progress.items?.map((item, index) => (
                            <div
                                key={item.plan_item_id}
                                className={`preparation-topic-card ${item.status === "completed"
                                        ? "preparation-topic-completed"
                                        : ""
                                    }`}
                            >
                                <div className="preparation-topic-number">
                                    {String(index + 1).padStart(2, "0")}
                                </div>

                                <div className="preparation-topic-main">
                                    <div className="preparation-topic-top">
                                        <div>
                                            <div className="preparation-topic-title-row">
                                                <h3>
                                                    {item.topic}
                                                </h3>

                                                <span
                                                    className={getPriorityClass(
                                                        item.priority
                                                    )}
                                                >
                                                    {item.priority}
                                                </span>
                                            </div>

                                            <div className="preparation-topic-skill">
                                                {item.skill}
                                            </div>
                                        </div>

                                        <div
                                            className={getStatusClass(
                                                item.status
                                            )}
                                        >
                                            <span className="status-dot" />
                                            {getStatusLabel(
                                                item.status
                                            )}
                                        </div>
                                    </div>

                                    <p className="preparation-topic-description">
                                        {item.description}
                                    </p>

                                    <div className="preparation-topic-footer">
                                        <div className="preparation-topic-meta">
                                            <span>
                                                ⏱{" "}
                                                {item.estimated_hours}{" "}
                                                hours
                                            </span>

                                            <span>
                                                Action:{" "}
                                                {item.action}
                                            </span>
                                        </div>

                                        <select
                                            value={item.status}
                                            disabled={
                                                updatingItem ===
                                                item.plan_item_id
                                            }
                                            onChange={(event) =>
                                                handleStatusChange(
                                                    item.plan_item_id,
                                                    event.target.value
                                                )
                                            }
                                            className="preparation-status-select"
                                        >
                                            <option value="not_started">
                                                Not Started
                                            </option>

                                            <option value="in_progress">
                                                In Progress
                                            </option>

                                            <option value="completed">
                                                Completed
                                            </option>
                                        </select>
                                    </div>

                                    {updatingItem ===
                                        item.plan_item_id && (
                                            <div className="preparation-updating">
                                                Saving progress...
                                            </div>
                                        )}
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}

export default PreparationProgress;