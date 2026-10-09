from dataclasses import dataclass

from dataclasses import dataclass
from typing import Literal


type LlmGemmaModel = Literal[
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
]


@dataclass(frozen=True, slots=True)
class LlmGemmaConfig:
    """Configuration for the Google Gemma LLM endpoint.

    Models:
        gemma-4-26b-a4b-it:
            25.2B parameter Mixture-of-Experts model with approximately
            3.8B active parameters per token. This substantially reduces
            inference compute compared with a similarly sized dense model
            while retaining the capacity of the larger expert network.

            Prefer this model for general-purpose use, batch processing,
            and workloads where latency and throughput are important.

            Approximate local inference memory requirements:
            BF16: 57.7 GB
            SFP8: 28.8 GB
            Q4:   14.4 GB

        gemma-4-31b-it:
            30.7B parameter dense model. All model parameters participate
            in inference, resulting in higher compute requirements and
            generally lower throughput than the 26B A4B model.

            Prefer this model where maximum reasoning and generation
            quality is more important than inference performance.

            Approximate local inference memory requirements:
            BF16: 69.9 GB
            SFP8: 34.9 GB
            Q4:   17.5 GB
    """

    model: LlmGemmaModel = "gemma-4-26b-a4b-it"