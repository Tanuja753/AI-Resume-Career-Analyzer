import math
import os
import re
from collections import Counter


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Local development keeps the existing SentenceTransformer behavior.
# Render can use "lightweight" to avoid loading PyTorch/SentenceTransformer.
MATCHING_MODE = os.getenv(
    "SEMANTIC_MATCHING_MODE",
    "transformer",
).lower()


class SemanticSkillMatcher:

    def __init__(self):

        self.model = None

        # ---------------------------------------------------------
        # TRANSFORMER MODE
        # ---------------------------------------------------------
        # This is the same model and behavior used by your project
        # before this deployment change.
        #
        # IMPORTANT:
        # SentenceTransformer is imported only when transformer
        # mode is actually selected. Therefore Render does not
        # load PyTorch when using lightweight mode.
        # ---------------------------------------------------------

        if MATCHING_MODE == "transformer":

            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(
                MODEL_NAME
            )

    # -------------------------------------------------------------
    # LIGHTWEIGHT TOKENIZATION
    # -------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> list[str]:

        return re.findall(
            r"\b[a-zA-Z0-9+#.]+\b",
            text.lower(),
        )

    # -------------------------------------------------------------
    # LIGHTWEIGHT TF-IDF-LIKE COSINE SIMILARITY
    # -------------------------------------------------------------

    @classmethod
    def _lightweight_similarity(
        cls,
        text1: str,
        text2: str,
    ) -> float:

        tokens1 = cls._tokenize(text1)
        tokens2 = cls._tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)

        vocabulary = set(counter1) | set(counter2)

        # Term-frequency vectors
        vector1 = []
        vector2 = []

        for term in vocabulary:

            vector1.append(
                counter1.get(term, 0)
            )

            vector2.append(
                counter2.get(term, 0)
            )

        # Cosine similarity
        dot_product = sum(
            a * b
            for a, b in zip(vector1, vector2)
        )

        magnitude1 = math.sqrt(
            sum(a * a for a in vector1)
        )

        magnitude2 = math.sqrt(
            sum(b * b for b in vector2)
        )

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        similarity = (
            dot_product
            / (magnitude1 * magnitude2)
        )

        return float(
            max(0.0, min(1.0, similarity))
        )

    # -------------------------------------------------------------
    # SIMILARITY CALCULATION
    # -------------------------------------------------------------

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:

        # ---------------------------------------------------------
        # EXISTING LOCAL TRANSFORMER BEHAVIOR
        # ---------------------------------------------------------

        if self.model is not None:

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

        # ---------------------------------------------------------
        # LIGHTWEIGHT DEPLOYMENT FALLBACK
        # ---------------------------------------------------------

        return self._lightweight_similarity(
            text1,
            text2,
        )


# -------------------------------------------------------------
# SINGLE SHARED MATCHER INSTANCE
# -------------------------------------------------------------

semantic_skill_matcher = SemanticSkillMatcher()

