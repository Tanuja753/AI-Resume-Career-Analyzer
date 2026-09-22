import { useEffect, useMemo, useState } from "react";

import SectionCard from "../components/dashboard/SectionCard";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";

import {
    generateInterviewQuestions,
    getInterviewQuestions,
} from "../services/dashboardService";

function InterviewPreparation() {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [activeCategory, setActiveCategory] =
        useState("all");

    async function loadQuestions() {
    try {
        setLoading(true);
        setError("");

        const resumeId =
            localStorage.getItem("resume_id");

        const jobDescriptionId =
            localStorage.getItem(
                "job_description_id"
            );

        if (!resumeId || !jobDescriptionId) {
            setError(
                "Resume or job description information is missing."
            );
            return;
        }

        // Step 1: Generate interview questions
        await generateInterviewQuestions(
            resumeId,
            jobDescriptionId
        );

        // Step 2: Load generated questions
        const data = await getInterviewQuestions(
            resumeId,
            jobDescriptionId
        );

        setQuestions(data.questions || []);
    } catch (err) {
        console.error(
            "Failed to generate/load interview questions:",
            err
        );

        setError(
            err.response?.data?.detail ||
                "Failed to generate interview questions."
        );
    } finally {
        setLoading(false);
    }
}

    useEffect(() => {
        loadQuestions();
    }, []);

    const categoryCounts = useMemo(() => {
        return {
            all: questions.length,
            technical: questions.filter(
                (question) =>
                    question.category === "technical"
            ).length,
            resume_specific: questions.filter(
                (question) =>
                    question.category === "resume_specific"
            ).length,
            behavioral: questions.filter(
                (question) =>
                    question.category === "behavioral"
            ).length,
            scenario: questions.filter(
                (question) =>
                    question.category === "scenario"
            ).length,
        };
    }, [questions]);

    const filteredQuestions = useMemo(() => {
        if (activeCategory === "all") {
            return questions;
        }

        return questions.filter(
            (question) =>
                question.category === activeCategory
        );
    }, [questions, activeCategory]);

    function getCategoryLabel(category) {
        if (category === "resume_specific") {
            return "Resume Specific";
        }

        if (category === "technical") {
            return "Technical";
        }

        if (category === "behavioral") {
            return "Behavioral";
        }

        if (category === "scenario") {
            return "Scenario";
        }

        return category;
    }

    function getDifficultyClass(difficulty) {
        if (difficulty === "easy") {
            return "interview-difficulty interview-difficulty-easy";
        }

        if (difficulty === "hard") {
            return "interview-difficulty interview-difficulty-hard";
        }

        return "interview-difficulty interview-difficulty-medium";
    }

    function getDifficultyLabel(difficulty) {
        if (!difficulty) {
            return "Medium";
        }

        return (
            difficulty.charAt(0).toUpperCase() +
            difficulty.slice(1)
        );
    }

    const categories = [
        {
            key: "all",
            label: "All Questions",
        },
        {
            key: "technical",
            label: "Technical",
        },
        {
            key: "resume_specific",
            label: "Resume Specific",
        },
        {
            key: "behavioral",
            label: "Behavioral",
        },
        {
            key: "scenario",
            label: "Scenario",
        },
    ];

    return (
        <div className="interview-page">
            <div className="interview-page-header">
                <div>
                    <div className="interview-eyebrow">
                        INTERVIEW PREPARATION
                    </div>

                    <h1>Prepare With Confidence</h1>

                    <p>
                        Practice personalized questions based on
                        your resume, target role, and skill gaps.
                    </p>
                </div>

                <div className="interview-header-stat">
                    <span>Questions available</span>

                    <strong>{questions.length}</strong>
                </div>
            </div>

            {loading && <Loading />}

            {!loading && error && (
                <ErrorMessage message={error} />
            )}

            {!loading && !error && questions.length === 0 && (
                <SectionCard title="No Questions Available">
                    <div className="interview-empty-state">
                        <h3>
                            Your interview questions are not
                            available yet.
                        </h3>

                        <p>
                            Generate personalized interview
                            questions after completing your
                            resume and job analysis.
                        </p>
                    </div>
                </SectionCard>
            )}

            {!loading &&
                !error &&
                questions.length > 0 && (
                    <>
                        <div className="interview-category-grid">
                            {categories.map((category) => (
                                <button
                                    key={category.key}
                                    type="button"
                                    className={`interview-category-card ${
                                        activeCategory ===
                                        category.key
                                            ? "interview-category-active"
                                            : ""
                                    }`}
                                    onClick={() =>
                                        setActiveCategory(
                                            category.key
                                        )
                                    }
                                >
                                    <span>
                                        {category.label}
                                    </span>

                                    <strong>
                                        {
                                            categoryCounts[
                                                category.key
                                            ]
                                        }
                                    </strong>
                                </button>
                            ))}
                        </div>

                        <div className="interview-section-heading">
                            <div>
                                <h2>
                                    {getCategoryLabel(
                                        activeCategory
                                    )}
                                </h2>

                                <p>
                                    Work through these questions
                                    and practice explaining your
                                    answers clearly.
                                </p>
                            </div>

                            <div className="interview-question-count">
                                {
                                    filteredQuestions.length
                                }{" "}
                                question
                                {filteredQuestions.length !==
                                1
                                    ? "s"
                                    : ""}
                            </div>
                        </div>

                        <div className="interview-question-list">
                            {filteredQuestions.map(
                                (question, index) => (
                                    <div
                                        key={question.id}
                                        className="interview-question-card"
                                    >
                                        <div className="interview-question-number">
                                            {String(
                                                index + 1
                                            ).padStart(2, "0")}
                                        </div>

                                        <div className="interview-question-content">
                                            <div className="interview-question-top">
                                                <div className="interview-question-badges">
                                                    <span className="interview-category-badge">
                                                        {getCategoryLabel(
                                                            question.category
                                                        )}
                                                    </span>

                                                    <span
                                                        className={getDifficultyClass(
                                                            question.difficulty
                                                        )}
                                                    >
                                                        {getDifficultyLabel(
                                                            question.difficulty
                                                        )}
                                                    </span>
                                                </div>

                                                <span className="interview-question-source">
                                                    AI Generated
                                                </span>
                                            </div>

                                            <h3>
                                                {
                                                    question.question
                                                }
                                            </h3>

                                            <div className="interview-practice-note">
                                                <span>
                                                    Practice
                                                </span>

                                                <p>
                                                    Think through
                                                    your answer,
                                                    explain your
                                                    reasoning, and
                                                    connect it to
                                                    your actual
                                                    project or
                                                    experience.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )
                            )}
                        </div>
                    </>
                )}
        </div>
    );
}

export default InterviewPreparation;