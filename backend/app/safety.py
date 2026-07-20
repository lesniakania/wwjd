import re
from dataclasses import dataclass

from .localization import Language


@dataclass(frozen=True)
class SafetyResult:
    needs_support: bool
    message: str | None = None


URGENT_PATTERNS = (
    r"\b(kill myself|end my life|suicide|want to die|self[- ]?harm)\b",
    r"\b(immediate danger|about to hurt|going to kill|weapon|threatened to kill)\b",
    r"\b(domestic violence|being abused|sexual abuse|child abuse|raped|assaulted)\b",
    r"\b(samobójstwo|zabić się|odebrać sobie życie|samookalecz|chcę umrzeć)\b",
    r"\b(bezpośrednie niebezpieczeństwo|grozi mi|chce mnie zabić|broń)\b",
    r"\b(przemoc domowa|molestowan|wykorzystywan|zgwałcon|znęcan)\b",
)


def check_safety(text: str, language: Language = "en") -> SafetyResult:
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in URGENT_PATTERNS):
        if language == "pl":
            message = (
                "Twoje bezpośrednie bezpieczeństwo jest ważniejsze niż ta refleksja. Jeśli komuś "
                "grozi niebezpieczeństwo, skontaktuj się teraz z numerem alarmowym 112 oraz z zaufaną "
                "osobą lub wykwalifikowanym specjalistą. Nie traktuj tej aplikacji jako zastępstwa pomocy."
            )
        else:
            message = (
                "Your immediate safety matters more than this reflection. If anyone is in danger, "
                "contact local emergency services now and reach a trusted person or qualified crisis, "
                "medical, or safeguarding professional. Do not use this app as a substitute for help."
            )
        return SafetyResult(
            needs_support=True,
            message=message,
        )
    return SafetyResult(needs_support=False)
