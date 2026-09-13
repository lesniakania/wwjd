import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import numpy as np


class Theme(StrEnum):
    ANGER = "anger"
    HONESTY = "honesty"
    FORGIVENESS = "forgiveness"
    CONFLICT = "conflict"
    FEAR = "fear"
    GENEROSITY = "generosity"
    PREJUDICE = "prejudice"
    DISCERNMENT = "discernment"
    GRIEF = "grief"
    LONELINESS = "loneliness"
    REPENTANCE = "repentance"
    HOPE = "hope"
    ENVY = "envy"
    HUMILITY = "humility"
    SELF_CONTROL = "self_control"
    JUSTICE = "justice"
    RESPONSIBILITY = "responsibility"
    COMPASSION = "compassion"
    BOUNDARIES_CONSENT_PRIVACY = "boundaries_consent_privacy"
    DIGNITY_AND_RESPECT = "dignity_and_respect"
    STEWARDSHIP = "stewardship"


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
    Theme.GRIEF: ThemeRule(
        _compile(
            r"\bgrie(?:f|ving)\b",
            r"\bbereav\w*",
            r"\bmourn\w*",
            r"\bżałob\w*",
            r"\bosieroc\w*",
        ),
        _compile(r"\bdeath\b", r"\bdied\b", r"\bśmier\w*", r"\bzmar\w*"),
    ),
    Theme.LONELINESS: ThemeRule(
        _compile(
            r"\blonel\w*",
            r"\bisolat\w*",
            r"\babandon\w*",
            r"\bsamotn\w*",
            r"\bopuszcz\w*",
            r"\bodrzucon\w*",
        )
    ),
    Theme.REPENTANCE: ThemeRule(
        _compile(
            r"\brepent\w*",
            r"\bremorse\w*",
            r"\bcontrition\b",
            r"\bżałuj\w*",
            r"\bskruch\w*",
            r"\bpokut\w*",
        ),
        _compile(r"\bnaprawić\b", r"\bpoprawić\b", r"\bmake amends\b"),
    ),
    Theme.HOPE: ThemeRule(
        _compile(
            r"\bhope(?:ful|less|lessness)?\b",
            r"\bdespair\w*",
            r"\bnadziej\w*",
            r"\bbeznadziej\w*",
            r"\brozpacz\w*",
        )
    ),
    Theme.ENVY: ThemeRule(
        _compile(
            r"\benv(?:y|ious)\w*",
            r"\bjealous\w*",
            r"\bzazdro\w*",
            r"\bzawiś\w*",
        )
    ),
    Theme.HUMILITY: ThemeRule(
        _compile(
            r"\bhumil(?:ity|ble)\w*",
            r"\barrogan\w*",
            r"\bpych\w*",
            r"\bpyszn\w*",
            r"\bpokor\w*",
        ),
        _compile(r"\bpride\b", r"\bproud\b", r"\bdum\w*"),
    ),
    Theme.SELF_CONTROL: ThemeRule(
        _compile(
            r"\bself[- ]control\b",
            r"\btempt\w*",
            r"\baddict\w*",
            r"\bcompuls\w*",
            r"\bsamokontrol\w*",
            r"\bpokus\w*",
            r"\buzależn\w*",
            r"\bnałog\w*",
        )
    ),
    Theme.JUSTICE: ThemeRule(
        _compile(
            r"\binjustice\w*",
            r"\bunfair\w*",
            r"\bjustice\b",
            r"\bniesprawiedliw\w*",
            r"\bsprawiedliwoś\w*",
        )
    ),
    Theme.RESPONSIBILITY: ThemeRule(
        _compile(
            r"\bresponsib\w*",
            r"\baccountab\w*",
            r"\bcommitment\w*",
            r"\bodpowiedzial\w*",
            r"\bzobowiąza\w*",
            r"\bobowiąz\w*",
        )
    ),
    Theme.COMPASSION: ThemeRule(
        _compile(
            r"\bcompassion\w*",
            r"\bmerciful\w*",
            r"\bwspółczu\w*",
            r"\bmiłosier\w*",
            r"\blitoś\w*",
        ),
        _compile(r"\bsuffer\w*", r"\bcierpi\w*", r"\bhelp\w*", r"\bpomóc\w*"),
    ),
    Theme.BOUNDARIES_CONSENT_PRIVACY: ThemeRule(
        _compile(
            r"\bpersonal boundar\w*",
            r"\b(?:without|against) (?:my|his|her|their|informed )?consent\b",
            r"\bunconsent\w*",
            r"\bprivacy\b",
            r"\bprivate (?:space|information|data)\b",
            r"\bgranic\w* osobist\w*",
            r"\bbez (?:\w+\s+){0,3}zgody\b",
            r"\bniechcian\w* (?:kontakt|dotyk)\w*",
            r"\bprywatnoś\w*",
            r"\bnarusz\w* prywat\w*",
        ),
        _compile(
            r"\bconsent\b",
            r"\bpermission\b",
            r"\bkontakt\w* fizyczn\w*",
            r"\bprywatn\w* (?:przestrze\w*|informac\w*|dan\w*)",
        ),
    ),
    Theme.DIGNITY_AND_RESPECT: ThemeRule(
        _compile(
            r"\bhuman dignity\b",
            r"\bdehumani[sz]\w*",
            r"\bhumiliat\w*",
            r"\bpublic(?:ly)? shame\w*",
            r"\bgodnoś\w* (?:człowieka|ludzk\w*|inn\w*|drug\w*)",
            r"\bponiż\w*",
            r"\bupokarz\w*",
            r"\bpogard\w*",
        ),
        _compile(
            r"\bdisrespect\w*",
            r"\bexclude\w*",
            r"\bbrak\w* szacunk\w*",
            r"\bwyklucz\w*",
        ),
    ),
    Theme.STEWARDSHIP: ThemeRule(
        _compile(
            r"\benvironmental (?:harm|responsibility|stewardship)\b",
            r"\bnatural resources?\b",
            r"\bshared resources?\b",
            r"\bwaste management\b",
            r"\bzanieczyszcz\w*",
            r"\bśrodowisk\w*",
            r"\bzasob\w* naturaln\w*",
            r"\bwspóln\w* zasob\w*",
            r"\bgospodar\w* odpad\w*",
            r"\bmarnotraw\w* (?:wod\w*|żywnoś\w*|zasob\w*|energ\w*)",
        ),
        _compile(
            r"\bstewardship\b",
            r"\bcommon good\b",
            r"\bdobro wspóln\w*",
            r"\bodpowiedzialn\w* korzyst\w* z zasob\w*",
        ),
    ),
}

THEME_PROFILES: dict[Theme, tuple[str, ...]] = {
    Theme.ANGER: (
        "Gniew prowadzący do chęci odwetu, zemsty lub publicznego upokorzenia drugiej osoby.",
        "Silna złość sprawia, że chcę zranić kogoś słowami albo odpowiedzieć tym samym.",
        "Anger leading to retaliation, revenge, humiliation, or the desire to hurt someone.",
    ),
    Theme.HONESTY: (
        "Dylemat dotyczący kłamstwa, oszustwa, zatajenia prawdy albo przypisania sobie cudzej zasługi.",
        "Wybór pomiędzy powiedzeniem prawdy a uzyskaniem korzyści dzięki nieuczciwości.",
        "A dilemma about lying, deception, hiding the truth, or taking credit for another person's work.",
    ),
    Theme.FORGIVENESS: (
        "Trudność z przebaczeniem osobie, która zraniła, zdradziła lub zawiodła zaufanie.",
        "Noszenie urazy i pytanie, czy wybaczyć krzywdę wyrządzoną przez drugiego człowieka.",
        "Struggling to forgive someone who caused harm, betrayal, or a lasting grievance.",
    ),
    Theme.CONFLICT: (
        "Spór między ludźmi, eskalacja kłótni oraz potrzeba pokojowego rozwiązania konfliktu.",
        "Konfrontacja, wzajemne oskarżenia i trudność w spokojnym wysłuchaniu drugiej strony.",
        "An interpersonal dispute, escalating argument, confrontation, or need for reconciliation.",
    ),
    Theme.FEAR: (
        "Lęk, niepokój i zamartwianie się przyszłością lub sytuacją, której nie można kontrolować.",
        "Strach utrudniający podjęcie decyzji i odzyskanie pokoju.",
        "Fear, anxiety, or persistent worry about the future and circumstances beyond one's control.",
    ),
    Theme.GENEROSITY: (
        "Decyzja, czy podzielić się pieniędzmi, czasem lub majątkiem z osobą w potrzebie.",
        "Chciwość przeciwstawiona hojności i konkretnej trosce o biednych.",
        "Choosing generosity and practical care for someone in need over greed or possessions.",
    ),
    Theme.PREJUDICE: (
        "Mam dość ludzi z tej grupy. Jedna osoba zachowała się źle, więc obwiniam wszystkich.",
        "Zbiorowe obwinianie całej społeczności za zachowanie pojedynczej osoby.",
        "Ocenianie człowieka gorzej tylko z powodu pochodzenia albo przynależności do grupy.",
        "Blaming a whole group for one person's actions or judging someone by their origin.",
    ),
    Theme.DISCERNMENT: (
        "Sprawdzanie prawdziwości nagrania, plotki lub wiadomości przed wydaniem osądu.",
        "Niepewna informacja z mediów społecznościowych, której źródło wymaga weryfikacji.",
        "Verifying a rumor, recording, allegation, or social-media claim before passing judgment.",
    ),
    Theme.GRIEF: (
        "Żałoba po śmierci bliskiej osoby, ból straty i potrzeba pocieszenia.",
        "Towarzyszenie komuś, kto opłakuje zmarłego i mierzy się z głębokim smutkiem.",
        "Grief, bereavement, mourning a loved one, and the need for comfort after loss.",
    ),
    Theme.LONELINESS: (
        "Samotność, poczucie opuszczenia i brak bliskiej osoby, z którą można porozmawiać.",
        "Poczucie odrzucenia lub izolacji i potrzeba przynależności do wspólnoty.",
        "Loneliness, isolation, abandonment, rejection, and the need to belong.",
    ),
    Theme.REPENTANCE: (
        "Żal z powodu wyrządzonego zła, przyjęcie odpowiedzialności i pragnienie naprawienia szkody.",
        "Szczera skrucha, przyznanie się do winy i decyzja o zmianie postępowania.",
        "Remorse, repentance, admitting wrongdoing, making amends, and choosing to change.",
    ),
    Theme.HOPE: (
        "Utrata nadziei w długotrwałej trudności i potrzeba wytrwałości mimo niepewności.",
        "Rozpacz oraz pytanie, czy cierpienie i obecna sytuacja mogą się jeszcze zmienić.",
        "Hope and perseverance in hardship, despair, or a situation that seems impossible to change.",
    ),
    Theme.ENVY: (
        "Zazdrość o sukces, relację lub majątek innej osoby i ciągłe porównywanie się z nią.",
        "Trudność z cieszeniem się dobrem drugiego człowieka z powodu zawiści.",
        "Inni mają lepiej ode mnie i zamiast cieszyć się ich sukcesem, czuję żal i niezadowolenie.",
        "Envy, jealousy, resentment of another person's good fortune, and constant comparison.",
    ),
    Theme.HUMILITY: (
        "Pycha utrudniająca przyznanie się do błędu, przeproszenie lub wysłuchanie drugiej osoby.",
        "Pragnienie uznania i wyższości przeciwstawione pokorze oraz służbie innym.",
        "Pride or arrogance contrasted with humility, service, and willingness to admit fault.",
    ),
    Theme.SELF_CONTROL: (
        "Powtarzająca się pokusa, nałóg lub impuls, któremu trudno się oprzeć.",
        "Brak samokontroli prowadzący do zachowania sprzecznego z własnymi wartościami.",
        "Temptation, addiction, compulsion, harmful impulses, and the struggle for self-control.",
    ),
    Theme.JUSTICE: (
        "Niesprawiedliwe traktowanie, stronnicza decyzja lub wykorzystywanie słabszej osoby.",
        "Pytanie, jak dochodzić sprawiedliwości bez odwetu i samemu postępować uczciwie.",
        "Injustice, unfair treatment, partiality, exploitation, and seeking justice without revenge.",
    ),
    Theme.RESPONSIBILITY: (
        "Unikanie odpowiedzialności za własną decyzję, obowiązek lub złożone zobowiązanie.",
        "Potrzeba rzetelnego wykonania powierzonego zadania i dotrzymania danego słowa.",
        "Responsibility, accountability, keeping commitments, and faithfully completing one's duty.",
    ),
    Theme.COMPASSION: (
        "Dostrzeżenie cierpienia drugiej osoby i decyzja o okazaniu jej konkretnej pomocy.",
        "Współczucie i miłosierdzie wyrażone obecnością oraz działaniem wobec potrzebującego.",
        "Compassion and mercy expressed through practical help and presence with someone suffering.",
    ),
    Theme.BOUNDARIES_CONSENT_PRIVACY: (
        "Poszanowanie osobistych granic, świadomej zgody oraz prywatnych przestrzeni i informacji.",
        "Naruszenie czyjejś prywatności, kontakt bez zgody albo zlekceważenie wyraźnej granicy.",
        "Respect for personal boundaries, informed consent, and private spaces and information.",
    ),
    Theme.DIGNITY_AND_RESPECT: (
        "Uznawanie godności innych osób i unikanie poniżania, wykluczania oraz pogardy.",
        "Publiczne upokorzenie lub traktowanie człowieka tak, jakby nie zasługiwał na szacunek.",
        "Recognizing human dignity and avoiding humiliation, exclusion, contempt, and disrespect.",
    ),
    Theme.STEWARDSHIP: (
        "Troska o środowisko, wspólne zasoby i przestrzenie powierzone wspólnej odpowiedzialności.",
        "Marnotrawienie lub niszczenie dóbr wspólnych przeciwstawione odpowiedzialnemu gospodarowaniu.",
        "Care for the environment, shared resources, and spaces entrusted to common responsibility.",
    ),
}


def enrich_theme_profiles(
    base_profiles: dict[Theme, tuple[str, ...]],
) -> dict[Theme, tuple[str, ...]]:
    data_path = Path(__file__).parent / "data"
    alignment = json.loads(
        (data_path / "theme_candidate_alignment.json").read_text(encoding="utf-8")
    )
    if alignment["status"] != "approved":
        raise ValueError("Theme candidate alignment must be approved before production use")
    candidates = json.loads((data_path / "theme_candidates.json").read_text(encoding="utf-8"))
    candidates_by_id = {candidate["id"]: candidate for candidate in candidates}
    enriched = {theme: list(profiles) for theme, profiles in base_profiles.items()}

    for group in alignment["covered_by_existing"]:
        summaries = [
            summary
            for candidate_id in group["candidate_ids"]
            for summary in (
                candidates_by_id[candidate_id]["summary_pl"],
                candidates_by_id[candidate_id]["summary_en"],
            )
        ]
        for theme_name in group["existing_themes"]:
            enriched[Theme(theme_name)].extend(summaries)

    for proposal in alignment["new_theme_proposals"]:
        theme = Theme(proposal["id"])
        enriched[theme].extend(
            summary
            for candidate_id in proposal["candidate_ids"]
            for summary in (
                candidates_by_id[candidate_id]["summary_pl"],
                candidates_by_id[candidate_id]["summary_en"],
            )
        )
    return {theme: tuple(dict.fromkeys(profiles)) for theme, profiles in enriched.items()}


THEME_PROFILES = enrich_theme_profiles(THEME_PROFILES)

STRONG_SIGNAL_CONFIDENCE = 0.9
SUPPORTING_SIGNAL_CONFIDENCE = 0.4
MINIMUM_CONFIDENCE = 0.65
MAXIMUM_CONFIDENCE = 1.0
SEMANTIC_THEME_THRESHOLD = 0.32


class ThemeEncoder(Protocol):
    def encode(self, texts: str | list[str]) -> np.ndarray: ...


class SemanticThemeRouter:
    """Infer at most one implicit ethical theme from general bilingual profiles."""

    def __init__(
        self,
        encoder: ThemeEncoder,
        threshold: float = SEMANTIC_THEME_THRESHOLD,
        minimum_margin: float = 0.05,
    ):
        self.encoder = encoder
        self.threshold = threshold
        self.minimum_margin = minimum_margin
        profiles = [
            (theme, profile)
            for theme, theme_profiles in THEME_PROFILES.items()
            for profile in theme_profiles
        ]
        self._profile_themes = [theme for theme, _ in profiles]
        self.profile_texts = [profile for _, profile in profiles]
        self._profile_embeddings = encoder.encode(self.profile_texts)

    def classify(self, text: str, excluded: set[Theme] | None = None) -> dict[Theme, float]:
        similarities = self._profile_embeddings @ self.encoder.encode(text)
        excluded_themes = excluded or set()
        eligible_indexes = [
            index
            for index, theme in enumerate(self._profile_themes)
            if theme not in excluded_themes
        ]
        if not eligible_indexes:
            return {}
        best_index = max(eligible_indexes, key=lambda index: float(similarities[index]))
        confidence = float(similarities[best_index])
        winning_theme = self._profile_themes[best_index]
        runner_up = max(
            (float(similarities[index]) for index in eligible_indexes
             if self._profile_themes[index] != winning_theme),
            default=-1.0,
        )
        if confidence < self.threshold or confidence - runner_up < self.minimum_margin:
            return {}
        return {winning_theme: confidence}


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
