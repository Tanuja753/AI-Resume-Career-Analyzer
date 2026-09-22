import { useEffect, useState } from "react";
import SectionCard from "../components/dashboard/SectionCard";
import api from "../services/api";


/* =========================================================
   RESUME BUILDER
========================================================= */

export default function ResumeBuilder() {
    const [drafts, setDrafts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [creating, setCreating] = useState(false);
    const [createError, setCreateError] = useState("");

    const [deletingId, setDeletingId] = useState(null);
    const [deleteError, setDeleteError] = useState("");

    const [selectedResume, setSelectedResume] = useState(null);

    useEffect(() => {
        fetchDrafts();
    }, []);

    const fetchDrafts = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get(
                "/resume-builder/drafts"
            );

            setDrafts(response.data || []);
        } catch (err) {
            console.error(
                "Failed to fetch drafts:",
                err
            );

            if (err.response?.status === 401) {
                setError(
                    "Your session has expired. Please login again."
                );
            } else {
                setError(
                    err.response?.data?.detail ||
                    "Failed to load resume drafts."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCreateDraft = async () => {
        try {
            setCreating(true);
            setCreateError("");

            const storedResumeId =
                localStorage.getItem("resume_id");

            const storedJobDescriptionId =
                localStorage.getItem(
                    "job_description_id"
                );

            if (!storedResumeId) {
                setCreateError(
                    "No resume found. Please upload and process a resume first."
                );
                return;
            }

            if (!storedJobDescriptionId) {
                setCreateError(
                    "No job description found. Please process a job description first."
                );
                return;
            }

            const resumeId = Number(storedResumeId);
            const jobDescriptionId = Number(
                storedJobDescriptionId
            );

            if (
                !Number.isInteger(resumeId) ||
                resumeId <= 0
            ) {
                setCreateError("Invalid resume ID.");
                return;
            }

            if (
                !Number.isInteger(jobDescriptionId) ||
                jobDescriptionId <= 0
            ) {
                setCreateError(
                    "Invalid job description ID."
                );
                return;
            }

            const payload = {
                source_resume_id: resumeId,
                job_description_id: jobDescriptionId,
                title: "My Resume",
            };

            const response = await api.post(
                "/resume-builder/drafts",
                payload
            );

            const newDraft = response.data;

            setDrafts((prev) => [
                newDraft,
                ...prev,
            ]);

            setSelectedResume(newDraft);
        } catch (err) {
            console.error(
                "Failed to create draft:",
                err
            );

            if (err.response?.status === 401) {
                setCreateError(
                    "Your session has expired. Please login again."
                );
            } else if (
                err.response?.status === 400
            ) {
                setCreateError(
                    err.response?.data?.detail ||
                    "Invalid resume or job description."
                );
            } else if (
                err.response?.status === 404
            ) {
                setCreateError(
                    err.response?.data?.detail ||
                    "Resume or job description was not found."
                );
            } else {
                setCreateError(
                    err.response?.data?.detail ||
                    "Failed to create resume draft."
                );
            }
        } finally {
            setCreating(false);
        }
    };

    const handleEditDraft = async (draftId) => {
        try {
            setError("");

            const response = await api.get(
                `/resume-builder/drafts/${draftId}`
            );

            setSelectedResume(response.data);
        } catch (err) {
            console.error(
                "Failed to open draft:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to open resume draft."
            );
        }
    };

    const handleDeleteDraft = async (draftId) => {
        const confirmed = window.confirm(
            "Are you sure you want to delete this resume draft?"
        );

        if (!confirmed) {
            return;
        }

        try {
            setDeletingId(draftId);
            setDeleteError("");

            await api.delete(
                `/resume-builder/drafts/${draftId}`
            );

            setDrafts((prev) =>
                prev.filter(
                    (draft) => draft.id !== draftId
                )
            );

            if (
                selectedResume?.id === draftId
            ) {
                setSelectedResume(null);
            }
        } catch (err) {
            console.error(
                "Failed to delete draft:",
                err
            );

            setDeleteError(
                err.response?.data?.detail ||
                "Failed to delete resume draft."
            );
        } finally {
            setDeletingId(null);
        }
    };

    /* -----------------------------------------------------
       OPEN EDITOR
    ----------------------------------------------------- */

    if (selectedResume) {
        return (
            <ResumeEditor
                resumeData={selectedResume}
                onBack={() => {
                    setSelectedResume(null);
                    fetchDrafts();
                }}
            />
        );
    }

    /* -----------------------------------------------------
       DRAFT LIST
    ----------------------------------------------------- */

    return (
        <div className="resume-builder-page">

            <div className="resume-builder-hero">

                <div className="resume-builder-hero-content">

                    <div className="resume-builder-eyebrow">
                        CAREER TOOLS
                    </div>

                    <h1>Resume Builder</h1>

                    <p>
                        Build, customize and generate an
                        ATS-friendly resume tailored to
                        your target job.
                    </p>

                </div>

                <button
                    className="primary-button resume-create-button"
                    onClick={handleCreateDraft}
                    disabled={creating}
                >
                    {creating
                        ? "Creating..."
                        : "+ Create Resume"}
                </button>

            </div>

            {createError && (
                <div className="error-message">
                    {createError}
                </div>
            )}

            {deleteError && (
                <div className="error-message">
                    {deleteError}
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {loading ? (
                <SectionCard title="Your Resume Drafts">
                    <div className="resume-loading-state">
                        <div className="loading-spinner"></div>

                        <p>
                            Loading your resume drafts...
                        </p>
                    </div>
                </SectionCard>
            ) : drafts.length === 0 ? (

                <SectionCard title="Your Resume Drafts">

                    <div className="resume-empty-state">

                        <div className="resume-empty-icon">
                            📄
                        </div>

                        <h3>
                            Create Your First Resume
                        </h3>

                        <p>
                            Your processed resume and
                            target job description are
                            ready. Create a resume draft
                            and start customizing it.
                        </p>

                        <button
                            className="primary-button"
                            onClick={
                                handleCreateDraft
                            }
                            disabled={creating}
                        >
                            {creating
                                ? "Creating..."
                                : "Create Your First Resume"}
                        </button>

                    </div>

                </SectionCard>

            ) : (

                <SectionCard title="Your Resume Drafts">

                    <div className="resume-drafts-list">

                        {drafts.map((draft) => (

                            <div
                                className="resume-draft-card"
                                key={draft.id}
                            >

                                <div className="draft-card-main">

                                    <div className="draft-file-icon">
                                        📄
                                    </div>

                                    <div className="draft-card-info">

                                        <h3>
                                            {draft.title ||
                                                "Untitled Resume"}
                                        </h3>

                                        <div className="draft-meta">

                                            <span
                                                className={`draft-status draft-status-${String(
                                                    draft.status ||
                                                        "draft"
                                                ).toLowerCase()}`}
                                            >
                                                {draft.status ||
                                                    "Draft"}
                                            </span>

                                            <span>
                                                Created{" "}
                                                {draft.created_at
                                                    ? new Date(
                                                          draft.created_at
                                                      ).toLocaleDateString()
                                                    : "N/A"}
                                            </span>

                                        </div>

                                    </div>

                                </div>

                                <div className="draft-actions">

                                    <button
                                        className="primary-button"
                                        onClick={() =>
                                            handleEditDraft(
                                                draft.id
                                            )
                                        }
                                    >
                                        Open Resume
                                    </button>

                                    <button
                                        className="danger-button"
                                        onClick={() =>
                                            handleDeleteDraft(
                                                draft.id
                                            )
                                        }
                                        disabled={
                                            deletingId ===
                                            draft.id
                                        }
                                    >
                                        {deletingId ===
                                        draft.id
                                            ? "Deleting..."
                                            : "Delete"}
                                    </button>

                                </div>

                            </div>

                        ))}

                    </div>

                </SectionCard>
            )}

        </div>
    );
}


/* =========================================================
   RESUME EDITOR
========================================================= */

function ResumeEditor({
    resumeData,
    onBack,
}) {
    const [resume, setResume] =
        useState(resumeData);

    const [previewMode, setPreviewMode] =
        useState(false);

    const [saving, setSaving] =
        useState(false);

    const [saveMessage, setSaveMessage] =
        useState("");

    const [saveError, setSaveError] =
        useState("");

    const [validating, setValidating] =
        useState(false);

    const [validationResult, setValidationResult] =
        useState(null);

    const [validationError, setValidationError] =
        useState("");

    const content =
        resume.content || {};

    /* -----------------------------------------------------
       EDITOR STATE
    ----------------------------------------------------- */

    const [personalInfo, setPersonalInfo] =
        useState(
            content.personal_info || {
                name: "",
                email: "",
                phone: "",
                location: "",
                linkedin: "",
                github: "",
            }
        );

    const [summary, setSummary] =
        useState(
            content.summary || ""
        );

    const [skills, setSkills] =
        useState(
            Array.isArray(content.skills)
                ? content.skills
                : []
        );

    const [experience, setExperience] =
        useState(
            Array.isArray(
                content.experience
            )
                ? content.experience
                : []
        );

    const [projects, setProjects] =
        useState(
            Array.isArray(
                content.projects
            )
                ? content.projects
                : []
        );

    const [education, setEducation] =
        useState(
            Array.isArray(
                content.education
            )
                ? content.education
                : []
        );

    const [certifications, setCertifications] =
        useState(
            Array.isArray(
                content.certifications
            )
                ? content.certifications
                : []
        );

    /* -----------------------------------------------------
       PERSONAL INFO
    ----------------------------------------------------- */

    const updatePersonalInfo = (
        field,
        value
    ) => {
        setPersonalInfo((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    /* -----------------------------------------------------
       SKILLS
    ----------------------------------------------------- */

    const updateSkill = (
        index,
        value
    ) => {
        setSkills((prev) =>
            prev.map((skill, i) =>
                i === index
                    ? value
                    : skill
            )
        );
    };

    const addSkill = () => {
        setSkills((prev) => [
            ...prev,
            "",
        ]);
    };

    const removeSkill = (
        index
    ) => {
        setSkills((prev) =>
            prev.filter(
                (_, i) => i !== index
            )
        );
    };

    /* -----------------------------------------------------
       EXPERIENCE
    ----------------------------------------------------- */

    const updateExperience = (
        index,
        field,
        value
    ) => {
        setExperience((prev) =>
            prev.map((item, i) =>
                i === index
                    ? {
                          ...item,
                          [field]: value,
                      }
                    : item
            )
        );
    };

    const addExperience = () => {
        setExperience((prev) => [
            ...prev,
            {
                role: "",
                company: "",
                duration: "",
                description: "",
            },
        ]);
    };

    const removeExperience = (
        index
    ) => {
        setExperience((prev) =>
            prev.filter(
                (_, i) => i !== index
            )
        );
    };

    /* -----------------------------------------------------
       PROJECTS
    ----------------------------------------------------- */

    const updateProject = (
        index,
        field,
        value
    ) => {
        setProjects((prev) =>
            prev.map((item, i) =>
                i === index
                    ? {
                          ...item,
                          [field]: value,
                      }
                    : item
            )
        );
    };

    const addProject = () => {
        setProjects((prev) => [
            ...prev,
            {
                name: "",
                description: "",
                technologies: [],
            },
        ]);
    };

    const removeProject = (
        index
    ) => {
        setProjects((prev) =>
            prev.filter(
                (_, i) => i !== index
            )
        );
    };

    const updateProjectTechnology = (
        projectIndex,
        technologyIndex,
        value
    ) => {
        setProjects((prev) =>
            prev.map((project, i) => {
                if (
                    i !== projectIndex
                ) {
                    return project;
                }

                const technologies =
                    Array.isArray(
                        project.technologies
                    )
                        ? project.technologies
                        : [];

                return {
                    ...project,
                    technologies:
                        technologies.map(
                            (
                                technology,
                                techIndex
                            ) =>
                                techIndex ===
                                technologyIndex
                                    ? value
                                    : technology
                        ),
                };
            })
        );
    };

    const addProjectTechnology = (
        projectIndex
    ) => {
        setProjects((prev) =>
            prev.map((project, i) => {
                if (
                    i !== projectIndex
                ) {
                    return project;
                }

                const technologies =
                    Array.isArray(
                        project.technologies
                    )
                        ? project.technologies
                        : [];

                return {
                    ...project,
                    technologies: [
                        ...technologies,
                        "",
                    ],
                };
            })
        );
    };

    const removeProjectTechnology = (
        projectIndex,
        technologyIndex
    ) => {
        setProjects((prev) =>
            prev.map((project, i) => {
                if (
                    i !== projectIndex
                ) {
                    return project;
                }

                const technologies =
                    Array.isArray(
                        project.technologies
                    )
                        ? project.technologies
                        : [];

                return {
                    ...project,
                    technologies:
                        technologies.filter(
                            (
                                _,
                                techIndex
                            ) =>
                                techIndex !==
                                technologyIndex
                        ),
                };
            })
        );
    };

    /* -----------------------------------------------------
       EDUCATION
    ----------------------------------------------------- */

    const updateEducation = (
        index,
        field,
        value
    ) => {
        setEducation((prev) =>
            prev.map((item, i) =>
                i === index
                    ? {
                          ...item,
                          [field]: value,
                      }
                    : item
            )
        );
    };

    const addEducation = () => {
        setEducation((prev) => [
            ...prev,
            {
                degree: "",
                institution: "",
                year: "",
                details: "",
            },
        ]);
    };

    const removeEducation = (
        index
    ) => {
        setEducation((prev) =>
            prev.filter(
                (_, i) => i !== index
            )
        );
    };

    /* -----------------------------------------------------
       CERTIFICATIONS
    ----------------------------------------------------- */

    const updateCertification = (
        index,
        field,
        value
    ) => {
        setCertifications((prev) =>
            prev.map((item, i) =>
                i === index
                    ? {
                          ...item,
                          [field]: value,
                      }
                    : item
            )
        );
    };

    const addCertification = () => {
        setCertifications((prev) => [
            ...prev,
            {
                name: "",
                issuer: "",
                year: "",
            },
        ]);
    };

    const removeCertification = (
        index
    ) => {
        setCertifications((prev) =>
            prev.filter(
                (_, i) => i !== index
            )
        );
    };

    /* -----------------------------------------------------
       BUILD RESUME CONTENT
    ----------------------------------------------------- */

    const buildResumeContent = () => {
        return {
            personal_info:
                personalInfo,

            summary:
                summary,

            skills:
                skills
                    .map((skill) =>
                        typeof skill ===
                        "string"
                            ? skill.trim()
                            : skill
                    )
                    .filter(
                        (skill) =>
                            skill &&
                            skill.length > 0
                    ),

            experience:
                experience,

            projects:
                projects.map(
                    (project) => ({
                        ...project,
                        technologies:
                            Array.isArray(
                                project.technologies
                            )
                                ? project.technologies
                                      .map(
                                          (
                                              technology
                                          ) =>
                                              typeof technology ===
                                              "string"
                                                  ? technology.trim()
                                                  : technology
                                      )
                                      .filter(
                                          (
                                              technology
                                          ) =>
                                              technology &&
                                              technology.length >
                                                  0
                                      )
                                : [],
                    })
                ),

            education:
                education,

            certifications:
                certifications,
        };
    };

    /* -----------------------------------------------------
       SAVE
    ----------------------------------------------------- */

    const handleSave = async () => {
        try {
            setSaving(true);
            setSaveMessage("");
            setSaveError("");

            const updatedContent =
                buildResumeContent();

            const payload = {
                title: resume.title,
                content:
                    updatedContent,
            };

            const response =
                await api.put(
                    `/resume-builder/drafts/${resume.id}`,
                    payload
                );

            setResume(response.data);

            setSaveMessage(
                "Resume saved successfully."
            );
        } catch (err) {
            console.error(
                "Failed to save resume:",
                err
            );

            setSaveError(
                err.response?.data
                    ?.detail ||
                    "Failed to save resume."
            );
        } finally {
            setSaving(false);
        }
    };

    /* -----------------------------------------------------
       VALIDATE
    ----------------------------------------------------- */

    const handleValidate = async () => {
        try {
            setValidating(true);
            setValidationResult(null);
            setValidationError("");

            const response =
                await api.post(
                    `/resume-builder/drafts/${resume.id}/validate`
                );

            setValidationResult(
                response.data
            );
        } catch (err) {
            console.error(
                "Failed to validate resume:",
                err
            );

            setValidationError(
                err.response?.data
                    ?.detail ||
                    "Failed to validate resume."
            );
        } finally {
            setValidating(false);
        }
    };

    /* -----------------------------------------------------
       PREVIEW MODE
    ----------------------------------------------------- */

    if (previewMode) {
        return (
            <ResumePreview
                resume={{
                    ...resume,
                    content:
                        buildResumeContent(),
                }}
                onBack={() =>
                    setPreviewMode(false)
                }
            />
        );
    }

    /* -----------------------------------------------------
       EDITOR UI
    ----------------------------------------------------- */

    return (
        <div className="resume-editor-page">

            {/* -------------------------------------------------
                EDITOR HEADER
            ------------------------------------------------- */}

            <div className="resume-editor-header">

                <div className="resume-editor-header-left">

                    <button
                        className="back-button"
                        onClick={onBack}
                    >
                        ← Back to Resumes
                    </button>

                    <div className="resume-builder-eyebrow">
                        RESUME EDITOR
                    </div>

                    <h1>
                        Build Your Resume
                    </h1>

                    <p>
                        Customize your resume
                        content and create a
                        professional ATS-friendly
                        version.
                    </p>

                </div>

                <div className="editor-actions">

                    <button
                        className="secondary-button"
                        onClick={() =>
                            setPreviewMode(true)
                        }
                    >
                        Preview
                    </button>

                    <button
                        className="secondary-button"
                        onClick={
                            handleValidate
                        }
                        disabled={
                            validating
                        }
                    >
                        {validating
                            ? "Validating..."
                            : "Validate"}
                    </button>

                    <button
                        className="primary-button"
                        onClick={
                            handleSave
                        }
                        disabled={saving}
                    >
                        {saving
                            ? "Saving..."
                            : "Save Resume"}
                    </button>

                </div>

            </div>

            {/* -------------------------------------------------
                MESSAGES
            ------------------------------------------------- */}

            {saveMessage && (
                <div className="success-message">
                    ✓ {saveMessage}
                </div>
            )}

            {saveError && (
                <div className="error-message">
                    {saveError}
                </div>
            )}

            {validationError && (
                <div className="error-message">
                    {validationError}
                </div>
            )}

            {/* -------------------------------------------------
                VALIDATION RESULT
            ------------------------------------------------- */}

            {validationResult && (
                <SectionCard title="Validation Result">

                    <div className="validation-result-wrapper">

                        <pre className="validation-result">
                            {JSON.stringify(
                                validationResult,
                                null,
                                2
                            )}
                        </pre>

                    </div>

                </SectionCard>
            )}

            {/* -------------------------------------------------
                00 RESUME DETAILS
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="00"
                title="Resume Details"
                description="Give your resume a clear title so you can identify it easily."
            >

                <InputField
                    label="Resume Title"
                    value={
                        resume.title || ""
                    }
                    placeholder="e.g. Python Backend Developer Resume"
                    onChange={(value) =>
                        setResume(
                            (prev) => ({
                                ...prev,
                                title: value,
                            })
                        )
                    }
                />

            </ResumeEditorSection>


            {/* -------------------------------------------------
                01 PERSONAL INFORMATION
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="01"
                title="Personal Information"
                description="Add the contact information you want recruiters to see."
            >

                <div className="form-grid">

                    <InputField
                        label="Full Name"
                        value={
                            personalInfo.name ||
                            ""
                        }
                        placeholder="Your full name"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "name",
                                value
                            )
                        }
                    />

                    <InputField
                        label="Email"
                        value={
                            personalInfo.email ||
                            ""
                        }
                        placeholder="you@example.com"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "email",
                                value
                            )
                        }
                    />

                    <InputField
                        label="Phone"
                        value={
                            personalInfo.phone ||
                            ""
                        }
                        placeholder="+91 XXXXX XXXXX"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "phone",
                                value
                            )
                        }
                    />

                    <InputField
                        label="Location"
                        value={
                            personalInfo.location ||
                            ""
                        }
                        placeholder="City, State"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "location",
                                value
                            )
                        }
                    />

                    <InputField
                        label="LinkedIn"
                        value={
                            personalInfo.linkedin ||
                            ""
                        }
                        placeholder="linkedin.com/in/yourname"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "linkedin",
                                value
                            )
                        }
                    />

                    <InputField
                        label="GitHub"
                        value={
                            personalInfo.github ||
                            ""
                        }
                        placeholder="github.com/yourusername"
                        onChange={(value) =>
                            updatePersonalInfo(
                                "github",
                                value
                            )
                        }
                    />

                </div>

            </ResumeEditorSection>


            {/* -------------------------------------------------
                02 SUMMARY
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="02"
                title="Professional Summary"
                description="Write a concise introduction highlighting your background, strengths and career direction."
            >

                <TextAreaField
                    label="Summary"
                    value={summary}
                    placeholder="Write a 2–4 line professional summary..."
                    onChange={setSummary}
                    rows={6}
                />

            </ResumeEditorSection>


            {/* -------------------------------------------------
                03 SKILLS
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="03"
                title="Skills"
                description="Add technical and relevant skills that match your target job description."
            >

                {skills.length === 0 ? (

                    <EmptyEditorSection
                        icon="✦"
                        title="No skills added"
                        description="Add your technical skills to strengthen your resume."
                        buttonText="+ Add First Skill"
                        onClick={addSkill}
                    />

                ) : (

                    <div className="skills-editor">

                        <div className="skills-chip-editor">

                            {skills.map(
                                (
                                    skill,
                                    index
                                ) => (

                                    <div
                                        className="skill-edit-chip"
                                        key={index}
                                    >

                                        <input
                                            type="text"
                                            value={
                                                skill ||
                                                ""
                                            }
                                            placeholder="Skill"
                                            onChange={(
                                                event
                                            ) =>
                                                updateSkill(
                                                    index,
                                                    event
                                                        .target
                                                        .value
                                                )
                                            }
                                        />

                                        <button
                                            type="button"
                                            className="skill-remove-button"
                                            onClick={() =>
                                                removeSkill(
                                                    index
                                                )
                                            }
                                            aria-label="Remove skill"
                                        >
                                            ×
                                        </button>

                                    </div>

                                )
                            )}

                        </div>

                        <button
                            className="add-item-button"
                            onClick={addSkill}
                        >
                            + Add Skill
                        </button>

                    </div>
                )}

            </ResumeEditorSection>


            {/* -------------------------------------------------
                04 EXPERIENCE
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="04"
                title="Experience"
                description="Add internships, work experience or other relevant professional experience."
            >

                {experience.length === 0 ? (

                    <EmptyEditorSection
                        icon="💼"
                        title="No experience added"
                        description="Add an internship or professional experience if you have one."
                        buttonText="+ Add Experience"
                        onClick={
                            addExperience
                        }
                    />

                ) : (

                    <div className="editor-items-list">

                        {experience.map(
                            (
                                item,
                                index
                            ) => (

                                <div
                                    className="resume-editor-item"
                                    key={index}
                                >

                                    <div className="editor-item-header">

                                        <div>

                                            <span className="editor-item-number">
                                                EXPERIENCE{" "}
                                                {String(
                                                    index +
                                                        1
                                                ).padStart(
                                                    2,
                                                    "0"
                                                )}
                                            </span>

                                            <h3>
                                                {item.role ||
                                                    "New Experience"}
                                            </h3>

                                        </div>

                                        <button
                                            className="remove-item-button"
                                            onClick={() =>
                                                removeExperience(
                                                    index
                                                )
                                            }
                                        >
                                            Remove
                                        </button>

                                    </div>

                                    <div className="form-grid">

                                        <InputField
                                            label="Role"
                                            value={
                                                item.role ||
                                                ""
                                            }
                                            placeholder="e.g. Software Engineering Intern"
                                            onChange={(
                                                value
                                            ) =>
                                                updateExperience(
                                                    index,
                                                    "role",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Company"
                                            value={
                                                item.company ||
                                                ""
                                            }
                                            placeholder="Company name"
                                            onChange={(
                                                value
                                            ) =>
                                                updateExperience(
                                                    index,
                                                    "company",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Duration"
                                            value={
                                                item.duration ||
                                                ""
                                            }
                                            placeholder="e.g. Jan 2026 – Feb 2026"
                                            onChange={(
                                                value
                                            ) =>
                                                updateExperience(
                                                    index,
                                                    "duration",
                                                    value
                                                )
                                            }
                                        />

                                    </div>

                                    <TextAreaField
                                        label="Description"
                                        value={
                                            item.description ||
                                            ""
                                        }
                                        placeholder="Describe your responsibilities, contributions and achievements..."
                                        onChange={(
                                            value
                                        ) =>
                                            updateExperience(
                                                index,
                                                "description",
                                                value
                                            )
                                        }
                                        rows={5}
                                    />

                                </div>

                            )
                        )}

                        <button
                            className="add-item-button"
                            onClick={
                                addExperience
                            }
                        >
                            + Add Another Experience
                        </button>

                    </div>
                )}

            </ResumeEditorSection>


            {/* -------------------------------------------------
                05 PROJECTS
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="05"
                title="Projects"
                description="Showcase projects that demonstrate your technical skills and problem-solving ability."
            >

                {projects.length === 0 ? (

                    <EmptyEditorSection
                        icon="🚀"
                        title="No projects added"
                        description="Add your strongest academic, personal or professional projects."
                        buttonText="+ Add Project"
                        onClick={
                            addProject
                        }
                    />

                ) : (

                    <div className="editor-items-list">

                        {projects.map(
                            (
                                project,
                                index
                            ) => {

                                const technologies =
                                    Array.isArray(
                                        project.technologies
                                    )
                                        ? project.technologies
                                        : [];

                                return (
                                    <div
                                        className="resume-editor-item"
                                        key={index}
                                    >

                                        <div className="editor-item-header">

                                            <div>

                                                <span className="editor-item-number">
                                                    PROJECT{" "}
                                                    {String(
                                                        index +
                                                            1
                                                    ).padStart(
                                                        2,
                                                        "0"
                                                    )}
                                                </span>

                                                <h3>
                                                    {project.name ||
                                                        "New Project"}
                                                </h3>

                                            </div>

                                            <button
                                                className="remove-item-button"
                                                onClick={() =>
                                                    removeProject(
                                                        index
                                                    )
                                                }
                                            >
                                                Remove
                                            </button>

                                        </div>

                                        <InputField
                                            label="Project Name"
                                            value={
                                                project.name ||
                                                ""
                                            }
                                            placeholder="e.g. AI Resume & Career Analyzer"
                                            onChange={(
                                                value
                                            ) =>
                                                updateProject(
                                                    index,
                                                    "name",
                                                    value
                                                )
                                            }
                                        />

                                        <TextAreaField
                                            label="Project Description"
                                            value={
                                                project.description ||
                                                ""
                                            }
                                            placeholder="Explain what you built, what problem it solves and your contribution..."
                                            onChange={(
                                                value
                                            ) =>
                                                updateProject(
                                                    index,
                                                    "description",
                                                    value
                                                )
                                            }
                                            rows={6}
                                        />

                                        <div className="project-technologies-editor">

                                            <div className="subsection-header">

                                                <div>

                                                    <label>
                                                        Technologies
                                                    </label>

                                                    <p>
                                                        Add the main technologies used in this project.
                                                    </p>

                                                </div>

                                            </div>

                                            {technologies.length ===
                                            0 ? (

                                                <button
                                                    className="add-item-button"
                                                    onClick={() =>
                                                        addProjectTechnology(
                                                            index
                                                        )
                                                    }
                                                >
                                                    + Add Technology
                                                </button>

                                            ) : (

                                                <div className="technology-list">

                                                    {technologies.map(
                                                        (
                                                            technology,
                                                            technologyIndex
                                                        ) => (

                                                            <div
                                                                className="technology-row"
                                                                key={
                                                                    technologyIndex
                                                                }
                                                            >

                                                                <InputField
                                                                    label={`Technology ${
                                                                        technologyIndex +
                                                                        1
                                                                    }`}
                                                                    value={
                                                                        technology ||
                                                                        ""
                                                                    }
                                                                    placeholder="e.g. FastAPI"
                                                                    onChange={(
                                                                        value
                                                                    ) =>
                                                                        updateProjectTechnology(
                                                                            index,
                                                                            technologyIndex,
                                                                            value
                                                                        )
                                                                    }
                                                                />

                                                                <button
                                                                    className="remove-small-button"
                                                                    onClick={() =>
                                                                        removeProjectTechnology(
                                                                            index,
                                                                            technologyIndex
                                                                        )
                                                                    }
                                                                >
                                                                    Remove
                                                                </button>

                                                            </div>

                                                        )
                                                    )}

                                                    <button
                                                        className="add-item-button"
                                                        onClick={() =>
                                                            addProjectTechnology(
                                                                index
                                                            )
                                                        }
                                                    >
                                                        + Add Technology
                                                    </button>

                                                </div>
                                            )}

                                        </div>

                                    </div>
                                );
                            }
                        )}

                        <button
                            className="add-item-button"
                            onClick={addProject}
                        >
                            + Add Another Project
                        </button>

                    </div>
                )}

            </ResumeEditorSection>


            {/* -------------------------------------------------
                06 EDUCATION
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="06"
                title="Education"
                description="Add your degree, college and academic details."
            >

                {education.length === 0 ? (

                    <EmptyEditorSection
                        icon="🎓"
                        title="No education added"
                        description="Add your academic qualification."
                        buttonText="+ Add Education"
                        onClick={
                            addEducation
                        }
                    />

                ) : (

                    <div className="editor-items-list">

                        {education.map(
                            (
                                item,
                                index
                            ) => (

                                <div
                                    className="resume-editor-item"
                                    key={index}
                                >

                                    <div className="editor-item-header">

                                        <div>

                                            <span className="editor-item-number">
                                                EDUCATION{" "}
                                                {String(
                                                    index +
                                                        1
                                                ).padStart(
                                                    2,
                                                    "0"
                                                )}
                                            </span>

                                            <h3>
                                                {item.degree ||
                                                    "New Education"}
                                            </h3>

                                        </div>

                                        <button
                                            className="remove-item-button"
                                            onClick={() =>
                                                removeEducation(
                                                    index
                                                )
                                            }
                                        >
                                            Remove
                                        </button>

                                    </div>

                                    <div className="form-grid">

                                        <InputField
                                            label="Degree"
                                            value={
                                                item.degree ||
                                                ""
                                            }
                                            placeholder="e.g. B.E. Computer Engineering"
                                            onChange={(
                                                value
                                            ) =>
                                                updateEducation(
                                                    index,
                                                    "degree",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Institution"
                                            value={
                                                item.institution ||
                                                ""
                                            }
                                            placeholder="College or university"
                                            onChange={(
                                                value
                                            ) =>
                                                updateEducation(
                                                    index,
                                                    "institution",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Year"
                                            value={
                                                item.year ||
                                                ""
                                            }
                                            placeholder="e.g. 2023 – 2027"
                                            onChange={(
                                                value
                                            ) =>
                                                updateEducation(
                                                    index,
                                                    "year",
                                                    value
                                                )
                                            }
                                        />

                                    </div>

                                    <TextAreaField
                                        label="Details"
                                        value={
                                            item.details ||
                                            ""
                                        }
                                        placeholder="CGPA, relevant coursework or other academic details..."
                                        onChange={(
                                            value
                                        ) =>
                                            updateEducation(
                                                index,
                                                "details",
                                                value
                                            )
                                        }
                                        rows={3}
                                    />

                                </div>

                            )
                        )}

                        <button
                            className="add-item-button"
                            onClick={
                                addEducation
                            }
                        >
                            + Add Another Education
                        </button>

                    </div>
                )}

            </ResumeEditorSection>


            {/* -------------------------------------------------
                07 CERTIFICATIONS
            ------------------------------------------------- */}

            <ResumeEditorSection
                number="07"
                title="Certifications"
                description="Add certifications, courses and relevant professional credentials."
            >

                {certifications.length === 0 ? (

                    <EmptyEditorSection
                        icon="🏆"
                        title="No certifications added"
                        description="Add relevant certifications or courses to strengthen your profile."
                        buttonText="+ Add Certification"
                        onClick={
                            addCertification
                        }
                    />

                ) : (

                    <div className="editor-items-list">

                        {certifications.map(
                            (
                                item,
                                index
                            ) => (

                                <div
                                    className="resume-editor-item"
                                    key={index}
                                >

                                    <div className="editor-item-header">

                                        <div>

                                            <span className="editor-item-number">
                                                CERTIFICATION{" "}
                                                {String(
                                                    index +
                                                        1
                                                ).padStart(
                                                    2,
                                                    "0"
                                                )}
                                            </span>

                                            <h3>
                                                {item.name ||
                                                    "New Certification"}
                                            </h3>

                                        </div>

                                        <button
                                            className="remove-item-button"
                                            onClick={() =>
                                                removeCertification(
                                                    index
                                                )
                                            }
                                        >
                                            Remove
                                        </button>

                                    </div>

                                    <div className="form-grid">

                                        <InputField
                                            label="Certification Name"
                                            value={
                                                item.name ||
                                                ""
                                            }
                                            placeholder="e.g. Generative AI Mastermind"
                                            onChange={(
                                                value
                                            ) =>
                                                updateCertification(
                                                    index,
                                                    "name",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Issuer"
                                            value={
                                                item.issuer ||
                                                ""
                                            }
                                            placeholder="Organization or platform"
                                            onChange={(
                                                value
                                            ) =>
                                                updateCertification(
                                                    index,
                                                    "issuer",
                                                    value
                                                )
                                            }
                                        />

                                        <InputField
                                            label="Year"
                                            value={
                                                item.year ||
                                                ""
                                            }
                                            placeholder="e.g. 2025"
                                            onChange={(
                                                value
                                            ) =>
                                                updateCertification(
                                                    index,
                                                    "year",
                                                    value
                                                )
                                            }
                                        />

                                    </div>

                                </div>

                            )
                        )}

                        <button
                            className="add-item-button"
                            onClick={
                                addCertification
                            }
                        >
                            + Add Another Certification
                        </button>

                    </div>
                )}

            </ResumeEditorSection>

            {/* -------------------------------------------------
                BOTTOM ACTION BAR
            ------------------------------------------------- */}

            <div className="resume-editor-bottom-actions">

                <button
                    className="secondary-button"
                    onClick={() =>
                        setPreviewMode(true)
                    }
                >
                    Preview Resume
                </button>

                <button
                    className="primary-button"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving
                        ? "Saving..."
                        : "Save Resume"}
                </button>

            </div>

        </div>
    );
}


/* =========================================================
   RESUME EDITOR SECTION
========================================================= */

function ResumeEditorSection({
    number,
    title,
    description,
    children,
}) {
    return (
        <section className="resume-editor-section">

            <div className="resume-section-heading">

                <div className="resume-section-number">
                    {number}
                </div>

                <div className="resume-section-heading-text">

                    <h2>
                        {title}
                    </h2>

                    <p>
                        {description}
                    </p>

                </div>

            </div>

            <div className="resume-section-body">
                {children}
            </div>

        </section>
    );
}


/* =========================================================
   EMPTY EDITOR SECTION
========================================================= */

function EmptyEditorSection({
    icon,
    title,
    description,
    buttonText,
    onClick,
}) {
    return (
        <div className="editor-empty-state">

            <div className="editor-empty-icon">
                {icon}
            </div>

            <h3>
                {title}
            </h3>

            <p>
                {description}
            </p>

            <button
                className="add-item-button"
                onClick={onClick}
            >
                {buttonText}
            </button>

        </div>
    );
}


/* =========================================================
   RESUME PREVIEW + PDF MANAGEMENT
========================================================= */

function ResumePreview({
    resume,
    onBack,
}) {
    const [generatingPdf, setGeneratingPdf] =
        useState(false);

    const [generatedPdf, setGeneratedPdf] =
        useState(null);

    const [generatedPdfs, setGeneratedPdfs] =
        useState([]);

    const [loadingPdfs, setLoadingPdfs] =
        useState(true);

    const [pdfError, setPdfError] =
        useState("");

    const content =
        resume.content || {};

    const personalInfo =
        content.personal_info || {};

    const summary =
        content.summary || "";

    const skills =
        Array.isArray(content.skills)
            ? content.skills
            : [];

    const experience =
        Array.isArray(
            content.experience
        )
            ? content.experience
            : [];

    const projects =
        Array.isArray(
            content.projects
        )
            ? content.projects
            : [];

    const education =
        Array.isArray(
            content.education
        )
            ? content.education
            : [];

    const certifications =
        Array.isArray(
            content.certifications
        )
            ? content.certifications
            : [];

    /* -----------------------------------------------------
       LOAD GENERATED PDFs
    ----------------------------------------------------- */

    useEffect(() => {
        fetchGeneratedPdfs();
    }, [resume.id]);

    const fetchGeneratedPdfs =
        async () => {
            try {
                setLoadingPdfs(true);
                setPdfError("");

                const response =
                    await api.get(
                        `/resume-pdf/drafts/${resume.id}`
                    );

                setGeneratedPdfs(
                    response.data || []
                );
            } catch (err) {
                console.error(
                    "Failed to fetch generated PDFs:",
                    err
                );

                setPdfError(
                    err.response?.data
                        ?.detail ||
                        "Failed to load generated PDFs."
                );
            } finally {
                setLoadingPdfs(false);
            }
        };

    /* -----------------------------------------------------
       SAVE + GENERATE PDF
    ----------------------------------------------------- */

    const handleGeneratePdf =
        async () => {
            try {
                setGeneratingPdf(true);
                setPdfError("");

                const latestContent =
                    resume.content || {};

                const saveResponse =
                    await api.put(
                        `/resume-builder/drafts/${resume.id}`,
                        {
                            title:
                                resume.title,
                            content:
                                latestContent,
                        }
                    );

                const savedResume =
                    saveResponse.data;

                setGeneratedPdf(null);

                const pdfResponse =
                    await api.post(
                        `/resume-pdf/drafts/${savedResume.id}/generate`
                    );

                const newPdf =
                    pdfResponse.data;

                setGeneratedPdf(
                    newPdf
                );

                setGeneratedPdfs(
                    (prev) => {
                        const alreadyExists =
                            prev.some(
                                (pdf) =>
                                    pdf.id ===
                                    newPdf.id
                            );

                        if (
                            alreadyExists
                        ) {
                            return prev;
                        }

                        return [
                            newPdf,
                            ...prev,
                        ];
                    }
                );
            } catch (err) {
                console.error(
                    "Failed to save or generate PDF:",
                    err
                );

                setPdfError(
                    err.response?.data
                        ?.detail ||
                        "Failed to save resume or generate PDF."
                );
            } finally {
                setGeneratingPdf(
                    false
                );
            }
        };

    /* -----------------------------------------------------
       DOWNLOAD PDF
    ----------------------------------------------------- */

    const handleDownloadPdf =
        async (pdf) => {
            if (!pdf?.id) {
                return;
            }

            try {
                setPdfError("");

                const response =
                    await api.get(
                        `/resume-pdf/${pdf.id}/download`,
                        {
                            responseType:
                                "blob",
                        }
                    );

                const blob =
                    new Blob(
                        [response.data],
                        {
                            type: "application/pdf",
                        }
                    );

                const url =
                    window.URL.createObjectURL(
                        blob
                    );

                const link =
                    document.createElement(
                        "a"
                    );

                link.href = url;

                link.download =
                    pdf.file_name ||
                    `resume_${resume.id}.pdf`;

                document.body.appendChild(
                    link
                );

                link.click();

                link.remove();

                window.URL.revokeObjectURL(
                    url
                );
            } catch (err) {
                console.error(
                    "Failed to download PDF:",
                    err
                );

                setPdfError(
                    err.response?.data
                        ?.detail ||
                        "Failed to download PDF."
                );
            }
        };

    return (
        <div className="resume-preview-page">

            {/* -------------------------------------------------
                PREVIEW HEADER
            ------------------------------------------------- */}

            <div className="resume-preview-header">

                <div>

                    <button
                        className="back-button"
                        onClick={onBack}
                    >
                        ← Back to Editor
                    </button>

                    <div className="resume-builder-eyebrow">
                        RESUME PREVIEW
                    </div>

                    <h1>
                        Review Your Resume
                    </h1>

                    <p>
                        Check the final layout
                        before generating your
                        ATS-friendly PDF.
                    </p>

                </div>

                <div className="editor-actions">

                    <button
                        className="primary-button"
                        onClick={
                            handleGeneratePdf
                        }
                        disabled={
                            generatingPdf
                        }
                    >
                        {generatingPdf
                            ? "Saving & Generating..."
                            : "Generate PDF"}
                    </button>

                    {generatedPdf && (
                        <button
                            className="secondary-button"
                            onClick={() =>
                                handleDownloadPdf(
                                    generatedPdf
                                )
                            }
                        >
                            Download Latest PDF
                        </button>
                    )}

                </div>

            </div>

            {pdfError && (
                <div className="error-message">
                    {pdfError}
                </div>
            )}

            {generatedPdf && (
                <div className="success-message">
                    ✓ PDF generated successfully:{" "}
                    <strong>
                        {generatedPdf.file_name}
                    </strong>
                </div>
            )}

            {/* -------------------------------------------------
                GENERATED PDFs
            ------------------------------------------------- */}

            <SectionCard title="Generated PDFs">

                {loadingPdfs ? (

                    <div className="resume-loading-state">

                        <div className="loading-spinner"></div>

                        <p>
                            Loading generated PDFs...
                        </p>

                    </div>

                ) : generatedPdfs.length ===
                  0 ? (

                    <div className="resume-empty-state compact">

                        <div className="resume-empty-icon">
                            📄
                        </div>

                        <h3>
                            No PDFs Generated Yet
                        </h3>

                        <p>
                            Generate your first PDF
                            from this resume and it
                            will appear here.
                        </p>

                    </div>

                ) : (

                    <div className="generated-pdf-list">

                        {generatedPdfs.map(
                            (pdf) => (

                                <div
                                    className="generated-pdf-card"
                                    key={pdf.id}
                                >

                                    <div className="generated-pdf-info">

                                        <div className="pdf-file-icon">
                                            PDF
                                        </div>

                                        <div>

                                            <h3>
                                                {pdf.file_name}
                                            </h3>

                                            <p>
                                                Generated{" "}
                                                {pdf.created_at
                                                    ? new Date(
                                                          pdf.created_at
                                                      ).toLocaleString()
                                                    : "N/A"}
                                            </p>

                                        </div>

                                    </div>

                                    <button
                                        className="secondary-button"
                                        onClick={() =>
                                            handleDownloadPdf(
                                                pdf
                                            )
                                        }
                                    >
                                        Download PDF
                                    </button>

                                </div>

                            )
                        )}

                    </div>
                )}

            </SectionCard>

            {/* -------------------------------------------------
                A4 RESUME PREVIEW
            ------------------------------------------------- */}

            <div className="resume-preview-workspace">

                <div className="preview-label">
                    A4 PREVIEW
                </div>

                <div className="resume-preview-container">

                    <div className="resume-paper">

                        {/* HEADER */}

                        <header className="resume-header">

                            <h1>
                                {personalInfo.name ||
                                    "Your Name"}
                            </h1>

                            <div className="resume-contact">

                                {personalInfo.email && (
                                    <span>
                                        {
                                            personalInfo.email
                                        }
                                    </span>
                                )}

                                {personalInfo.phone && (
                                    <span>
                                        {
                                            personalInfo.phone
                                        }
                                    </span>
                                )}

                                {personalInfo.location && (
                                    <span>
                                        {
                                            personalInfo.location
                                        }
                                    </span>
                                )}

                            </div>

                            <div className="resume-links">

                                {personalInfo.linkedin && (
                                    <span>
                                        {
                                            personalInfo.linkedin
                                        }
                                    </span>
                                )}

                                {personalInfo.github && (
                                    <span>
                                        {
                                            personalInfo.github
                                        }
                                    </span>
                                )}

                            </div>

                        </header>


                        {/* SUMMARY */}

                        {summary && (
                            <PreviewSection
                                title="Summary"
                            >
                                <p>
                                    {summary}
                                </p>
                            </PreviewSection>
                        )}


                        {/* SKILLS */}

                        {skills.length >
                            0 && (
                            <PreviewSection
                                title="Skills"
                            >

                                <div className="preview-skills">

                                    {skills.map(
                                        (
                                            skill,
                                            index
                                        ) => (
                                            <span
                                                key={
                                                    index
                                                }
                                            >
                                                {
                                                    skill
                                                }
                                            </span>
                                        )
                                    )}

                                </div>

                            </PreviewSection>
                        )}


                        {/* EXPERIENCE */}

                        {experience.length >
                            0 && (
                            <PreviewSection
                                title="Experience"
                            >

                                {experience.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <div
                                            className="preview-item"
                                            key={
                                                index
                                            }
                                        >

                                            <div className="preview-item-header">

                                                <strong>
                                                    {
                                                        item.role
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        item.duration
                                                    }
                                                </span>

                                            </div>

                                            {item.company && (
                                                <div className="preview-company">
                                                    {
                                                        item.company
                                                    }
                                                </div>
                                            )}

                                            {item.description && (
                                                <p>
                                                    {
                                                        item.description
                                                    }
                                                </p>
                                            )}

                                        </div>

                                    )
                                )}

                            </PreviewSection>
                        )}


                        {/* PROJECTS */}

                        {projects.length >
                            0 && (
                            <PreviewSection
                                title="Projects"
                            >

                                {projects.map(
                                    (
                                        project,
                                        index
                                    ) => (

                                        <div
                                            className="preview-item"
                                            key={
                                                index
                                            }
                                        >

                                            <strong>
                                                {
                                                    project.name
                                                }
                                            </strong>

                                            {project.description && (
                                                <p>
                                                    {
                                                        project.description
                                                    }
                                                </p>
                                            )}

                                            {Array.isArray(
                                                project.technologies
                                            ) &&
                                                project
                                                    .technologies
                                                    .length >
                                                    0 && (

                                                    <p className="preview-technologies">

                                                        <strong>
                                                            Technologies:
                                                        </strong>{" "}

                                                        {project.technologies.join(
                                                            ", "
                                                        )}

                                                    </p>
                                                )}

                                        </div>

                                    )
                                )}

                            </PreviewSection>
                        )}


                        {/* EDUCATION */}

                        {education.length >
                            0 && (
                            <PreviewSection
                                title="Education"
                            >

                                {education.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <div
                                            className="preview-item"
                                            key={
                                                index
                                            }
                                        >

                                            <div className="preview-item-header">

                                                <strong>
                                                    {
                                                        item.degree
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        item.year
                                                    }
                                                </span>

                                            </div>

                                            {item.institution && (
                                                <div className="preview-company">
                                                    {
                                                        item.institution
                                                    }
                                                </div>
                                            )}

                                            {item.details && (
                                                <p>
                                                    {
                                                        item.details
                                                    }
                                                </p>
                                            )}

                                        </div>

                                    )
                                )}

                            </PreviewSection>
                        )}


                        {/* CERTIFICATIONS */}

                        {certifications.length >
                            0 && (
                            <PreviewSection
                                title="Certifications"
                            >

                                {certifications.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <div
                                            className="preview-item"
                                            key={
                                                index
                                            }
                                        >

                                            <div className="preview-item-header">

                                                <strong>
                                                    {
                                                        item.name
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        item.year
                                                    }
                                                </span>

                                            </div>

                                            {item.issuer && (
                                                <div className="preview-company">
                                                    {
                                                        item.issuer
                                                    }
                                                </div>
                                            )}

                                        </div>

                                    )
                                )}

                            </PreviewSection>
                        )}

                    </div>

                </div>

            </div>

        </div>
    );
}


/* =========================================================
   PREVIEW SECTION
========================================================= */

function PreviewSection({
    title,
    children,
}) {
    return (
        <section className="resume-preview-section">

            <h2>
                {title}
            </h2>

            <div className="resume-section-content">
                {children}
            </div>

        </section>
    );
}


/* =========================================================
   INPUT FIELD
========================================================= */

function InputField({
    label,
    value,
    onChange,
    placeholder = "",
}) {
    return (
        <div className="form-field">

            <label>
                {label}
            </label>

            <input
                type="text"
                value={value ?? ""}
                placeholder={placeholder}
                onChange={(event) =>
                    onChange(
                        event.target.value
                    )
                }
            />

        </div>
    );
}


/* =========================================================
   TEXT AREA FIELD
========================================================= */

function TextAreaField({
    label,
    value,
    onChange,
    rows = 4,
    placeholder = "",
}) {
    return (
        <div className="form-field">

            <label>
                {label}
            </label>

            <textarea
                rows={rows}
                value={value ?? ""}
                placeholder={
                    placeholder
                }
                onChange={(event) =>
                    onChange(
                        event.target.value
                    )
                }
            />

        </div>
    );
}