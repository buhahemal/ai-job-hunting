"""Cosine similarity utilities for embedding-based job matching."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

Vector = Union[Sequence[float], np.ndarray]


def cosine_similarity(left: Vector, right: Vector) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns a value in [-1.0, 1.0]. For L2-normalized embeddings this equals the dot product.
    """
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)

    if a.shape != b.shape:
        raise ValueError(f'Vector shape mismatch: {a.shape} vs {b.shape}')
    if a.size == 0:
        raise ValueError('Cannot compute cosine similarity for empty vectors')

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def similarity_to_percentage(similarity: float) -> int:
    """Scale cosine similarity to an integer match percentage in [0, 100]."""
    clamped = max(0.0, min(1.0, float(similarity)))
    return int(round(clamped * 100))
