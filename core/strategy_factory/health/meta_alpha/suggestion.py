from dataclasses import dataclass


@dataclass(frozen=True)
class MetaAlphaSuggestion:
    """
    Advisory-only meta-alpha suggestion.

    NEVER binding.
    """

    message: str
    confidence: float
    advisory_only: bool = True
