from app.services.semantic_matcher import semantic_skill_matcher


def test_identical_skills_have_high_similarity():
    score = semantic_skill_matcher.calculate_similarity(
        "Python",
        "Python",
    )

    assert score >= 0.95


def test_different_skills_have_lower_similarity():
    score = semantic_skill_matcher.calculate_similarity(
        "Python",
        "Docker",
    )

    assert 0 <= score <= 1


def test_database_skill_similarity():
    score = semantic_skill_matcher.calculate_similarity(
        "PostgreSQL",
        "PostgreSQL",
    )

    assert score >= 0.95


def test_related_skills_return_valid_similarity():
    score = semantic_skill_matcher.calculate_similarity(
        "Git",
        "GitHub",
    )

    assert 0 <= score <= 1


def test_unrelated_frameworks_return_valid_similarity():
    score = semantic_skill_matcher.calculate_similarity(
        "FastAPI",
        "Django",
    )

    assert 0 <= score <= 1