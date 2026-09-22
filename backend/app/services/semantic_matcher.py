from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


class SemanticSkillMatcher:

    def __init__(self):

        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:

        embeddings = self.model.encode(
            [text1, text2],
            convert_to_tensor=True,
        )

        similarity = self.model.similarity(
            embeddings[0].unsqueeze(0),
            embeddings[1].unsqueeze(0),
        )

        return float(
            similarity.item()
        )


semantic_skill_matcher = (
    SemanticSkillMatcher()
)