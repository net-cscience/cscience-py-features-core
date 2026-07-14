from abc import ABC, abstractmethod


class EmbeddingBase(ABC):
    """Mixin for datatypes containing semantic embeddings."""

    @abstractmethod
    def length(self) -> int:
        """Return the shared embedding dimension."""

    def embedding_dim(self) -> int:
        """Return the shared embedding dimension."""
        return self.length()