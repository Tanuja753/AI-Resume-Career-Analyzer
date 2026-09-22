import api from "../api/axios";

export async function getResumeDrafts() {
    const response = await api.get("/resume-builder/drafts");
    return response.data;
}

export async function getPreparationPlan(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/preparation-plans/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}

export async function generatePreparationPlan(
    resumeId,
    jobDescriptionId
) {
    const response = await api.post(
        `/preparation-plans/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}

export async function getPreparationProgress(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/preparation-plans/resume/${resumeId}/job-description/${jobDescriptionId}/progress`
    );

    return response.data;
}

export async function updatePreparationProgress(
    planItemId,
    status,
    notes = null
) {
    const response = await api.patch(
        `/preparation-plans/items/${planItemId}/progress`,
        {
            status,
            notes,
        }
    );

    return response.data;
}

export async function getCompatibility(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/job-compatibility/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}

export async function getSkillGaps(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/skill-gaps/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}

export async function getInterviewQuestionCount(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/interview-questions/resume/${resumeId}/job-description/${jobDescriptionId}/count`
    );

    return response.data;
}

export async function getJobDescription(jobDescriptionId) {
    const response = await api.get(
        `/job-descriptions/${jobDescriptionId}`
    );

    return response.data;
}

export async function getInterviewQuestions(
    resumeId,
    jobDescriptionId
) {
    const response = await api.get(
        `/interview-questions/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}

export async function generateInterviewQuestions(
    resumeId,
    jobDescriptionId
) {
    const response = await api.post(
        `/interview-questions/resume/${resumeId}/job-description/${jobDescriptionId}`
    );

    return response.data;
}