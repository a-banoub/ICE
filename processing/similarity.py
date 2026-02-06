from __future__ import annotations

import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Compute text similarity using TF-IDF + cosine similarity.

    Uses fresh vectorizer per call to avoid memory accumulation.
    """

    def _create_vectorizer(self) -> TfidfVectorizer:
        """Create a fresh vectorizer for each computation."""
        return TfidfVectorizer(
            stop_words="english",
            max_features=1000,  # Reduced from 5000 to save memory
            ngram_range=(1, 2),
        )

    def compute_pairwise(self, texts: list[str]) -> list[list[float]]:
        """Return NxN similarity matrix for a list of texts."""
        if len(texts) < 2:
            return []
        try:
            # Fresh vectorizer each time to prevent memory leak
            vectorizer = self._create_vectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            result = cosine_similarity(tfidf_matrix).tolist()
            # Explicitly delete to help GC
            del vectorizer, tfidf_matrix
            return result
        except ValueError:
            logger.warning("TF-IDF vectorization failed (empty vocabulary?)")
            n = len(texts)
            return [[0.0] * n for _ in range(n)]

    def score(self, text_a: str, text_b: str) -> float:
        """Return cosine similarity between two texts."""
        try:
            vectorizer = self._create_vectorizer()
            tfidf = vectorizer.fit_transform([text_a, text_b])
            result = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            del vectorizer, tfidf
            return result
        except ValueError:
            return 0.0
