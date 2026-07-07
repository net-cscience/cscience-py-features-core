from abc import ABC

from .vector_base import VectorBase


class EmbeddingBase(VectorBase, ABC):
    """Mixin for semantic embedding vectors."""

    def embedding_dim(self) -> int:
        """Return the embedding dimension."""
        return self.length()