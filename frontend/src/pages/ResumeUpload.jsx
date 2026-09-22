import { useState } from "react";
import api from "../api/axios";

function ResumeUpload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];

        setError("");
        setMessage("");

        if (!selectedFile) {
            setFile(null);
            return;
        }

        const allowedTypes = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ];

        if (!allowedTypes.includes(selectedFile.type)) {
            setError("Please upload a PDF or DOCX file.");
            setFile(null);
            return;
        }

        setFile(selectedFile);
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a resume file first.");
            return;
        }

        setLoading(true);
        setError("");
        setMessage("");

        try {
            /* ------------------------------------------------
               STEP 1: Upload Resume
            ------------------------------------------------ */
            setMessage("Uploading your resume...");

            const formData = new FormData();
            formData.append("file", file);

            const uploadResponse = await api.post(
                "/resumes/upload",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            const resumeId = uploadResponse.data?.id;

            if (!resumeId) {
                throw new Error("Resume ID was not returned by the server.");
            }

            // Store the newly uploaded resume ID
            localStorage.setItem("resume_id", String(resumeId));

            // A new resume should not use an old job description
            localStorage.removeItem("job_description_id");

            /* ------------------------------------------------
               STEP 2: Extract Resume Text
            ------------------------------------------------ */
            setMessage("Extracting resume content...");

            await api.post(`/resumes/${resumeId}/extract`);

            /* ------------------------------------------------
               STEP 3: Structure Resume
            ------------------------------------------------ */
            setMessage("Structuring your resume...");

            await api.post(`/resumes/${resumeId}/structure`);

            /* ------------------------------------------------
               STEP 4: Extract Resume Skills
            ------------------------------------------------ */
            setMessage("Extracting technical and relevant skills...");

            await api.post(`/resumes/${resumeId}/skills`);

            /* ------------------------------------------------
               COMPLETE
            ------------------------------------------------ */
            setMessage(
                "Resume uploaded, processed, and skills extracted successfully."
            );

            setFile(null);

            // Reset file input if it has an id
            const fileInput = document.getElementById("resume-file-input");

            if (fileInput) {
                fileInput.value = "";
            }
        } catch (err) {
            console.error("Resume processing error:", err);

            if (err.response?.status === 401) {
                setError("Your session has expired. Please log in again.");
            } else if (err.response?.status === 400) {
                setError(
                    err.response?.data?.detail ||
                    "The uploaded resume could not be processed."
                );
            } else if (err.response?.status === 404) {
                setError(
                    "The resume processing endpoint was not found. Please check the backend."
                );
            } else {
                setError(
                    err.response?.data?.detail ||
                    err.message ||
                    "Something went wrong while processing your resume."
                );
            }

            setMessage("");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="resume-upload-page">

            <h1>Upload Resume</h1>

            <p>
                Upload your resume to extract your information and skills
                automatically.
            </p>

            <div className="resume-upload-card">

                <div className="resume-upload-input-area">

                    <label htmlFor="resume-file-input">
                        Select Resume
                    </label>

                    <input
                        id="resume-file-input"
                        type="file"
                        accept=".pdf,.docx"
                        onChange={handleFileChange}
                        disabled={loading}
                    />

                    {file && (
                        <div className="selected-file">
                            <strong>{file.name}</strong>
                            <span>
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </span>
                        </div>
                    )}

                </div>

                <button
                    type="button"
                    className="primary-button"
                    onClick={handleUpload}
                    disabled={loading || !file}
                >
                    {loading ? "Processing Resume..." : "Upload Resume"}
                </button>

                {message && (
                    <div className="success-message">
                        {message}
                    </div>
                )}

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

            </div>

        </div>
    );
}

export default ResumeUpload;