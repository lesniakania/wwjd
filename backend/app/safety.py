import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyResult:
    needs_support: bool
    message: str | None = None


URGENT_PATTERNS = (
    r"\b(kill myself|end my life|suicide|want to die|self[- ]?harm)\b",
    r"\b(immediate danger|about to hurt|going to kill|weapon|threatened to kill)\b",
    r"\b(domestic violence|being abused|sexual abuse|child abuse|raped|assaulted)\b",
)


def check_safety(text: str) -> SafetyResult:
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in URGENT_PATTERNS):
        return SafetyResult(
            needs_support=True,
            message=(
                "Your immediate safety matters more than this reflection. If anyone is in danger, "
                "contact local emergency services now and reach a trusted person or qualified crisis, "
                "medical, or safeguarding professional. Do not use this app as a substitute for help."
            ),
        )
    return SafetyResult(needs_support=False)

