import json
from pathlib import Path

import numpy as np
import pytest

from app.localization import THEME_LABELS, THEME_NAMES
from app.retrieval import THEME_ANCHORS
from app.themes import THEME_PROFILES, THEME_RULES, SemanticThemeRouter, Theme, ThemeClassifier


def test_classifier_returns_no_themes_for_unrelated_text() -> None:
    assert ThemeClassifier().classify("I need help choosing a new chair.") == set()


@pytest.mark.parametrize(
    ("text", "theme"),
    [
        ("Jestem wściekła i marzę o zemście.", Theme.ANGER),
        ("Okłamałem przyjaciela i chcę powiedzieć prawdę.", Theme.HONESTY),
        ("Nie potrafię wybaczyć komuś, kto mnie skrzywdził.", Theme.FORGIVENESS),
        ("Ciągle kłócę się ze współpracownikiem.", Theme.CONFLICT),
        ("Boję się przyszłości i bardzo się martwię.", Theme.FEAR),
        ("Chcę podzielić się pieniędzmi z potrzebującymi.", Theme.GENEROSITY),
        ("Potraktowałem go źle z powodu rasistowskiego uprzedzenia.", Theme.PREJUDICE),
        ("Podobno to nagranie jest prawdziwe, ale nie znam źródła.", Theme.DISCERNMENT),
        ("Jestem w żałobie po śmierci bliskiej osoby.", Theme.GRIEF),
        ("Czuję się samotny i opuszczony.", Theme.LONELINESS),
        ("Żałuję tego, co zrobiłem, i chcę się poprawić.", Theme.REPENTANCE),
        ("Straciłem nadzieję, że sytuacja może się poprawić.", Theme.HOPE),
        ("Zazdroszczę innym ich sukcesów.", Theme.ENVY),
        ("Moja pycha nie pozwala mi przyznać się do błędu.", Theme.HUMILITY),
        ("Nie umiem oprzeć się pokusie i tracę samokontrolę.", Theme.SELF_CONTROL),
        ("Zostałem potraktowany niesprawiedliwie.", Theme.JUSTICE),
        ("Nie dotrzymałem zobowiązania i unikam odpowiedzialności.", Theme.RESPONSIBILITY),
        ("Chcę okazać współczucie cierpiącej osobie.", Theme.COMPASSION),
        ("Lekarz wykonał zabieg bez mojej świadomej zgody.", Theme.BOUNDARIES_CONSENT_PRIVACY),
        ("Publicznie ją poniżyłem i podeptałem jej godność.", Theme.DIGNITY_AND_RESPECT),
        ("Marnujemy wspólne zasoby i zanieczyszczamy środowisko.", Theme.STEWARDSHIP),
    ],
)
def test_classifier_handles_common_polish_inflections(text: str, theme: Theme) -> None:
    assert theme in ThemeClassifier().classify(text)


@pytest.mark.parametrize(
    ("text", "theme"),
    [
        ("Kolega polecił mi bardzo wygodne krzesło.", Theme.CONFLICT),
        ("Chcę dać dziecku książkę na urodziny.", Theme.GENEROSITY),
        ("My friend sent me a photo from vacation.", Theme.CONFLICT),
        ("Mam dość Syryjczyków, wszyscy oni są podobno winni.", Theme.PREJUDICE),
        ("Zgadzam się na spotkanie jutro rano.", Theme.BOUNDARIES_CONSENT_PRIVACY),
        ("To film godny polecenia.", Theme.DIGNITY_AND_RESPECT),
        ("Zarządzam zasobami CSS w aplikacji.", Theme.STEWARDSHIP),
    ],
)
def test_classifier_does_not_classify_ambiguous_words_without_context(
    text: str,
    theme: Theme,
) -> None:
    assert theme not in ThemeClassifier().classify(text)


def test_classifier_exposes_confidence_for_retrieval() -> None:
    matches = ThemeClassifier().classify_with_confidence(
        "Nie wiem, czy wybaczyć zdradę, o której podobno mówią w mediach."
    )

    assert matches[Theme.FORGIVENESS] >= 0.8
    assert matches[Theme.DISCERNMENT] >= 0.8


def test_every_theme_has_rules_profiles_anchors_and_localized_names() -> None:
    themes = set(Theme)

    assert set(THEME_RULES) == themes
    assert set(THEME_PROFILES) == themes
    assert set(THEME_ANCHORS) == {str(theme) for theme in themes}
    assert set(THEME_NAMES["pl"]) == {str(theme) for theme in themes}
    assert set(THEME_NAMES["en"]) == {str(theme) for theme in themes}
    assert set(THEME_LABELS["pl"]) == {str(theme) for theme in themes}
    assert set(THEME_LABELS["en"]) == {str(theme) for theme in themes}
    assert len(themes) == 21


def test_approved_candidate_summaries_enrich_production_profiles() -> None:
    data = Path(__file__).parents[1] / "app" / "data"
    candidates = json.loads((data / "theme_candidates.json").read_text(encoding="utf-8"))
    all_profiles = {profile for profiles in THEME_PROFILES.values() for profile in profiles}

    for candidate in candidates:
        assert candidate["summary_pl"] in all_profiles
        assert candidate["summary_en"] in all_profiles


class ThemeProfileEncoder:
    def encode(self, texts: str | list[str]) -> np.ndarray:
        if isinstance(texts, list):
            return np.asarray([self._vector(text) for text in texts], dtype=np.float32)
        return np.asarray(self._vector(texts), dtype=np.float32)

    @staticmethod
    def _vector(text: str) -> list[float]:
        lowered = text.lower()
        if "zbiorow" in lowered or "whole group" in lowered or "całą grupę" in lowered:
            return [1.0, 0.0, 0.0]
        if "neutralna wzmianka" in lowered:
            return [0.0, 0.0, 1.0]
        return [0.0, 1.0, 0.0]


def test_semantic_router_detects_generalized_group_blame() -> None:
    router = SemanticThemeRouter(ThemeProfileEncoder())

    matches = router.classify(
        "Jedna osoba z tej społeczności zrobiła coś złego, więc obwiniam całą grupę."
    )

    assert matches == {Theme.PREJUDICE: 1.0}


def test_semantic_router_does_not_force_a_theme_for_an_unrelated_description() -> None:
    router = SemanticThemeRouter(ThemeProfileEncoder())

    assert router.classify("Neutralna wzmianka o spotkaniu sąsiadów.") == {}


class RankedThemeEncoder:
    def encode(self, texts: str | list[str]) -> np.ndarray:
        if isinstance(texts, list):
            return np.asarray([self._vector(text) for text in texts], dtype=np.float32)
        return np.asarray(self._vector(texts), dtype=np.float32)

    @staticmethod
    def _vector(text: str) -> list[float]:
        lowered = text.lower()
        if "zbiorow" in lowered or "whole group" in lowered:
            return [1.0, 0.0, 0.0]
        if "sprawdzanie prawdziwości" in lowered or "verifying a rumor" in lowered:
            return [0.0, 1.0, 0.0]
        if "dwa wymiary" in lowered:
            return [0.8, 1.0, 0.0]
        return [0.0, 0.0, -1.0]


def test_semantic_router_can_skip_a_theme_already_found_by_rules() -> None:
    router = SemanticThemeRouter(RankedThemeEncoder())

    matches = router.classify("Opis ma dwa wymiary.", excluded={Theme.DISCERNMENT})

    assert matches == {Theme.PREJUDICE: pytest.approx(0.8)}


class AmbiguousThemeEncoder:
    def encode(self, texts: str | list[str]) -> np.ndarray:
        if isinstance(texts, str):
            return np.asarray([1.0, 0.0])
        return np.asarray([[0.6, 0.0] for text in texts])


def test_semantic_router_abstains_when_themes_are_indistinguishable() -> None:
    router = SemanticThemeRouter(AmbiguousThemeEncoder())
    assert router.classify("A description with no clear ethical concern.") == {}
