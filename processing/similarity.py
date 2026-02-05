from __future__ import annotations

import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Compute text similarity using TF-IDF + cosine similarity."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )

    def compute_pairwise(self, texts: list[str]) -> list[list[float]]:
        """Return NxN similarity matrix for a list of texts."""
        if len(texts) < 2:
            return []
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            return cosine_similarity(tfidf_matrix).tolist()
        except ValueError:
            logger.warning("TF-IDF vectorization failed (empty vocabulary?)")
            n = len(texts)
            return [[0.0] * n for _ in range(n)]

    def score(self, text_a: str, text_b: str) -> float:
        """Return cosine similarity between two texts."""
        try:
            tfidf = self.vectorizer.fit_transform([text_a, text_b])
            return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        except ValueError:
            return 0.0
