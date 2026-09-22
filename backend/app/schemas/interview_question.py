from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


QuestionCategory = Literal[
    "technical",
    "resume_specific",
    "behavioral",
    "scenario",
]

QuestionDifficulty = Literal[
    "easy",
    "medium",
    "hard",
]


class GeneratedInterviewQuestion(BaseModel):

    category: QuestionCategory

    question: str = Field(
        min_length=10,
        max_length=1000,
    )

    difficulty: QuestionDifficulty


class GeneratedInterviewQuestions(BaseModel):

    questions: list[
        GeneratedInterviewQuestion
    ]


class InterviewQuestionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    resume_id: int
    job_description_id: int
    category: QuestionCategory
    question: str
    difficulty: QuestionDifficulty
    source: str


class InterviewQuestionGenerationResponse(BaseModel):

    resume_id: int
    job_description_id: int

    questions: list[
        InterviewQuestionResponse
    ]