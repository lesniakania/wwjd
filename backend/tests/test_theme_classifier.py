import pytest

from app.themes import Theme, ThemeClassifier


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
