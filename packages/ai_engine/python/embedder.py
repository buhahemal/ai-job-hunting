"""Lazy loader for the local sentence-transformers embedding model."""

from __future__ import annotations

import os
from typing import List, Optional

import numpy as np

DEFAULT_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

_model = None
_model_name: Optional[str] = None


def model_name() -> str:
    """Return the configured embedding model identifier."""
    return os.environ.get('AI_EMBEDDING_MODEL', DEFAULT_MODEL_NAME)


def get_embedder():
    """Load and cache the SentenceTransformer model."""
    global _model, _model_name
    target = model_name()
    if _model is not None and _model_name == target:
        return _model

    from sentence_transformers import SentenceTransformer

    print(f'[AIEmbedder] Loading embedding model: {target}')
    _model = SentenceTransformer(target)
    _model_name = target
    return _model


def encode_texts(texts: List[str]) -> np.ndarray:
    """Encode one or more strings into L2-normalized embedding vectors."""
    if not texts:
        raise ValueError('At least one text value is required for encoding')

    model = get_embedder()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype=np.float64)


def reset_embedder_cache() -> None:
    """Clear cached model state (used in tests)."""
    global _model, _model_name
    _model = None
    _model_name = None
