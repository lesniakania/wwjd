import re
from dataclasses import dataclass
from enum import StrEnum


class Theme(StrEnum):
    ANGER = "anger"
    HONESTY = "honesty"
    FORGIVENESS = "forgiveness"
    CONFLICT = "conflict"
    FEAR = "fear"
    GENEROSITY = "generosity"
    PREJUDICE = "prejudice"
    DISCERNMENT = "discernment"


@dataclass(frozen=True)
class ThemeRule:
    strong_patterns: tuple[re.Pattern[str], ...]
    supporting_patterns: tuple[re.Pattern[str], ...] = ()


def _compile(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)


THEME_RULES: dict[Theme, ThemeRule] = {
    Theme.ANGER: ThemeRule(
        _compile(
            r"\bang(?:er|ry)\b",
            r"\bfurious\b",
            r"\brevenge\b",
            r"\bretaliat\w*",
            r"\bembarrass\w*",
            r"\bhumiliat\w*",
            r"\bhate(?:d|ful)?\b",
            r"\bhatred\b",
            r"\bzł(?:oś\w*|[yae]\w*)",
            r"\bźl\w*",
            r"\bwściek\w*",
            r"\bgniew\w*",
            r"\bzemst\w*",
            r"\bupokorz\w*",
            r"\bośmiesz\w*",
            r"\bnienawi\w*",
        )
    ),
    Theme.HONESTY: ThemeRule(
        _compile(
            r"\blie[ds]?\b",
            r"\blying\b",
            r"\bdishonest\w*",
            r"\bdeceiv\w*",
            r"\bfraud\w*",
            r"\b(?:o|s)?kłam\w*",
            r"\buczciw\w*",
            r"\boszuk\w*",
        ),
        _compile(
            r"\bhonest\w*",
            r"\btruth\w*",
            r"\btook credit\b",
            r"\bprawd\w*",
            r"\bzasług\w*",
        ),
    ),
    Theme.FORGIVENESS: ThemeRule(
        _compile(
            r"\bforgiv\w*",
            r"\bgrudge\w*",
            r"\bbetray\w*",
            r"\bprzebacz\w*",
            r"\bwybacz\w*",
            r"\buraz\w*",
            r"\bzdrad\w*",
            r"\bskrzywd\w*",
        ),
        _compile(r"\bhurt\w*", r"\boffend\w*"),
    ),
    Theme.CONFLICT: ThemeRule(
        _compile(
            r"\bconflict\w*",
            r"\bquarrel\w*",
            r"\bconfront\w*",
            r"\bviolence\b",
            r"\bkonflikt\w*",
            r"\bkłó[ct]\w*",
            r"\bskonfront\w*",
            r"\bprzemoc\w*",
        ),
        _compile(
            r"\bargument\w*",
            r"\battack\w*",
            r"\bkłót\w*",
            r"\batak\w*",
            r"\bnie słuch\w*",
        ),
    ),
    Theme.FEAR: ThemeRule(
        _compile(
            r"\bafraid\b",
            r"\banxi(?:ous|ety)\b",
            r"\bfear\w*",
            r"\bworr(?:y|ied|ies)\b",
            r"\bstrach\w*",
            r"\bboj[ęą]\b",
            r"\bbać się\b",
            r"\blęk\w*",
            r"\bmartw\w*",
            r"\bniepok\w*",
        )
    ),
    Theme.GENEROSITY: ThemeRule(
        _compile(
            r"\bgeneros\w*",
            r"\bgreed\w*",
            r"\bcharit\w*",
            r"\bdonat\w*",
            r"\bhojn\w*",
            r"\bchciw\w*",
            r"\bjałmuż\w*",
            r"\bpodziel\w*\s+się\b",
            r"\bpotrzebując\w*",
        ),
        _compile(
            r"\bpoor\b",
            r"\bpoverty\b",
            r"\bpossessions?\b",
            r"\bmoney\b",
            r"\bbied\w*",
            r"\bpieni(?:ądz|ędz)\w*",
            r"\bmająt\w*",
        ),
    ),
    Theme.PREJUDICE: ThemeRule(
        _compile(
            r"\bprejudic\w*",
            r"\bracis\w*",
            r"\bxenophob\w*",
            r"\bdiscriminat\w*",
            r"\buprzedz\w*",
            r"\brasiz\w*",
            r"\brasist\w*",
            r"\bksenofob\w*",
            r"\bdyskrymin\w*",
        )
    ),
    Theme.DISCERNMENT: ThemeRule(
        _compile(
            r"\brumou?r\w*",
            r"\balleg\w*",
            r"\bmisinformation\w*",
            r"\bfact[- ]check\w*",
            r"\bplot\w*",
            r"\bpogłos\w*",
            r"\bdezinform\w*",
            r"\bpodobno\b",
        ),
        _compile(
            r"\bviral\w*",
            r"\bsocial media\b",
            r"\bmedi\w* społecznościow\w*",
            r"\bnews\b",
            r"\bclaim\w*",
            r"\btransmit\w*",
            r"\bnagran\w*",
            r"\binformac\w*",
            r"\bwiadomoś\w*",
            r"\bźródł\w*",
        ),
    ),
}

STRONG_SIGNAL_CONFIDENCE = 0.9
SUPPORTING_SIGNAL_CONFIDENCE = 0.4
MINIMUM_CONFIDENCE = 0.65
MAXIMUM_CONFIDENCE = 1.0


class ThemeClassifier:
    def classify(self, text: str) -> set[Theme]:
        return set(self.classify_with_confidence(text))

    def classify_with_confidence(self, text: str) -> dict[Theme, float]:
        matches: dict[Theme, float] = {}
        for theme, rule in THEME_RULES.items():
            strong_matches = self._match_count(text, rule.strong_patterns)
            supporting_matches = self._match_count(text, rule.supporting_patterns)
            confidence = self._confidence(strong_matches, supporting_matches)
            if confidence >= MINIMUM_CONFIDENCE:
                matches[theme] = confidence
        return matches

    @staticmethod
    def _match_count(text: str, patterns: tuple[re.Pattern[str], ...]) -> int:
        return sum(pattern.search(text) is not None for pattern in patterns)

    @staticmethod
    def _confidence(strong_matches: int, supporting_matches: int) -> float:
        if strong_matches:
            additional_evidence = 0.05 * (strong_matches - 1) + 0.025 * supporting_matches
            return min(MAXIMUM_CONFIDENCE, STRONG_SIGNAL_CONFIDENCE + additional_evidence)
        return min(MAXIMUM_CONFIDENCE, SUPPORTING_SIGNAL_CONFIDENCE * supporting_matches)
