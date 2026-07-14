from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NsfwPredictionData:
    """NSFW classification result for one image."""

    label: str
    score: float
    normal_score: float
    nsfw_score: float

    def is_nsfw(self, threshold: float = 0.5) -> bool:
        """Return whether the NSFW score is at or above the threshold."""
        return self.nsfw_score >= threshold
