from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LlmGemmaResultData:
    text: str