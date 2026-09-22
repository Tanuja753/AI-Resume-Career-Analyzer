import { useState } from "react";
import api from "../api/axios";

function JobDescription() {
    const [targetJobTitle, setTargetJobTitle] = useState("");
    const [description, setDescription] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setResult(null);

        if (!targetJobTitle.trim()) {
            setError("Please enter the target job title.");
            return;
        }

        if (description.trim().length < 50) {
            setError(
                "Job description must contain at least 50 characters."
            );
            return;
        }

        // Get the currently active structured resume
        const storedResumeId = localStorage.getItem("resume_id");

        if (!storedResumeId) {
            setError(
                "Please upload and structure a resume before processing a job description."
            );
            return;
        }

        const resumeId = Number(storedResumeId);

        if (!Number.isInteger(resumeId) || resumeId <= 0) {
            setError(
                "The stored resume ID is invalid. Please upload your resume again."
            );
            return;
        }

        try {
            setLoading(true);

            // ---------------------------------------------
            // STEP 1: Process Job Description
            // ---------------------------------------------

            const response = await api.post(
                "/job-descriptions/process",
                {
                    target_job_title: targetJobTitle.trim(),
                    description: description.trim(),
                    resume_id: resumeId,
                }
            );

            const jobDescriptionId = response.data.id;

            if (
                !Number.isInteger(Number(jobDescriptionId)) ||
                Number(jobDescriptionId) <= 0
            ) {
                setError(
                    "Job description was processed, but the returned ID is invalid."
                );
                return;
            }

            // ---------------------------------------------
            // STEP 2: Extract Job Description Skills
            // ---------------------------------------------

            await api.post(
                `/job-descriptions/${jobDescriptionId}/skills`
            );

            // ---------------------------------------------
            // STEP 3: Store active Job Description ID
            // ---------------------------------------------

            localStorage.setItem(
                "job_description_id",
                String(jobDescriptionId)
            );

            // ---------------------------------------------
            // COMPLETE
            // ---------------------------------------------

            setResult(response.data);

        } catch (err) {
            console.error(
                "Job description processing error:",
                err
            );

            if (err.response?.status === 401) {
                setError(
                    "Your session has expired. Please login again."
                );
            } else if (err.response?.status === 400) {
                setError(
                    err.response?.data?.detail ||
                    "Invalid job description."
                );
            } else if (err.response?.status === 404) {
                setError(
                    err.response?.data?.detail ||
                    "Resume or job description resource was not found."
                );
            } else {
                setError(
                    err.response?.data?.detail ||
                    "Failed to process job description."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-page">

            <header className="dashboard-header">
                <div>
                    <h1>Job Description</h1>

                    <p>
                        Enter the job you want to analyze your
                        resume against.
                    </p>
                </div>
            </header>

            <main className="dashboard-content">

                <div className="dashboard-card">

                    <form onSubmit={handleSubmit}>

                        <div className="form-group">

                            <label>
                                Target Job Title
                            </label>

                            <input
                                type="text"
                                value={targetJobTitle}
                                onChange={(event) =>
                                    setTargetJobTitle(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. Python Backend Developer"
                                disabled={loading}
                            />

                        </div>

                        <div className="form-group">

                            <label>
                                Job Description
                            </label>

                            <textarea
                                value={description}
                                onChange={(event) =>
                                    setDescription(
                                        event.target.value
                                    )
                                }
                                placeholder="Paste the complete job description here..."
                                rows={15}
                                disabled={loading}
                            />

                        </div>

                        {error && (
                            <p className="error-message">
                                {error}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Processing..."
                                : "Process Job Description"}
                        </button>

                    </form>

                </div>

                {result && (
                    <div className="dashboard-card">

                        <h2>
                            Job Description Processed
                        </h2>

                        <p>
                            Status: {result.status}
                        </p>

                        <p>
                            Job Description ID: {result.id}
                        </p>

                        <p className="success-message">
                            Job description processed and required
                            skills extracted successfully.
                        </p>

                        <h3>
                            Structured Information
                        </h3>

                        <pre>
                            {JSON.stringify(
                                result.structured_data,
                                null,
                                2
                            )}
                        </pre>

                    </div>
                )}

            </main>

        </div>
    );
}

export default JobDescription;