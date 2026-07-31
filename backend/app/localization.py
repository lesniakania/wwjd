from typing import Literal


Language = Literal["pl", "en"]

POLISH_BOOKS = {
    "Genesis": "Rodzaju", "Exodus": "Wyjścia", "Leviticus": "Kapłańska",
    "Numbers": "Liczb", "Deuteronomy": "Powtórzonego Prawa", "Joshua": "Jozuego",
    "Judges": "Sędziów", "Ruth": "Rut", "1 Samuel": "1 Samuela", "2 Samuel": "2 Samuela",
    "1 Kings": "1 Królewska", "2 Kings": "2 Królewska", "1 Chronicles": "1 Kronik",
    "2 Chronicles": "2 Kronik", "Ezra": "Ezdrasza", "Nehemiah": "Nehemiasza",
    "Esther": "Estery", "Tobit": "Tobiasza", "Judith": "Judyty",
    "1 Maccabees": "1 Machabejska", "2 Maccabees": "2 Machabejska",
    "Wisdom": "Mądrości", "Sirach": "Mądrości Syracha", "Baruch": "Barucha",
    "Job": "Hioba", "Psalms": "Psalmów", "Proverbs": "Przysłów",
    "Ecclesiastes": "Kaznodziei", "Song of Solomon": "Pieśń nad Pieśniami",
    "Isaiah": "Izajasza", "Jeremiah": "Jeremiasza", "Lamentations": "Lamentacje",
    "Ezekiel": "Ezechiela", "Daniel": "Daniela", "Hosea": "Ozeasza", "Joel": "Joela",
    "Amos": "Amosa", "Obadiah": "Abdiasza", "Jonah": "Jonasza", "Micah": "Micheasza",
    "Nahum": "Nahuma", "Habakkuk": "Habakuka", "Zephaniah": "Sofoniasza",
    "Haggai": "Aggeusza", "Zechariah": "Zachariasza", "Malachi": "Malachiasza",
    "Matthew": "Mateusza", "Mark": "Marka", "Luke": "Łukasza", "John": "Jana",
    "Acts": "Dzieje Apostolskie", "Romans": "Rzymian", "1 Corinthians": "1 Koryntian",
    "2 Corinthians": "2 Koryntian", "Galatians": "Galacjan", "Ephesians": "Efezjan",
    "Philippians": "Filipian", "Colossians": "Kolosan", "1 Thessalonians": "1 Tesaloniczan",
    "2 Thessalonians": "2 Tesaloniczan", "1 Timothy": "1 Tymoteusza",
    "2 Timothy": "2 Tymoteusza", "Titus": "Tytusa", "Philemon": "Filemona",
    "Hebrews": "Hebrajczyków", "James": "Jakuba", "1 Peter": "1 Piotra",
    "2 Peter": "2 Piotra", "1 John": "1 Jana", "2 John": "2 Jana", "3 John": "3 Jana",
    "Jude": "Judy", "Revelation": "Objawienie",
}


def reference(book: str, chapter: int, verse_start: int, verse_end: int, language: Language) -> str:
    localized_book = POLISH_BOOKS.get(book, book) if language == "pl" else book
    verses = str(verse_start) if verse_start == verse_end else f"{verse_start}–{verse_end}"
    return f"{localized_book} {chapter}:{verses}"


def translation_name(language: Language) -> str:
    if language == "pl":
        return "Uwspółcześniona Biblia Gdańska (UBG), © 2018 Fundacja Wrota Nadziei, CC BY-ND 4.0"
    return "World English Bible, Catholic Edition (WEBC), public domain"


THEME_LABELS = {
    "pl": {
        "anger": "Gniew i odwet",
        "honesty": "Prawda i uczciwość",
        "forgiveness": "Przebaczenie i pojednanie",
        "conflict": "Konflikt i pojednanie",
        "fear": "Lęk i zaufanie",
        "generosity": "Hojność i troska",
        "prejudice": "Bezstronność i miłość ponad podziałami",
        "discernment": "Rozeznawanie informacji",
        "grief": "Żałoba i pocieszenie",
        "loneliness": "Samotność i przynależność",
        "repentance": "Skrucha i naprawienie krzywdy",
        "hope": "Nadzieja i wytrwałość",
        "envy": "Zazdrość i wdzięczność",
        "humility": "Pycha i pokora",
        "self_control": "Pokusa i samokontrola",
        "justice": "Sprawiedliwość",
        "responsibility": "Odpowiedzialność",
        "compassion": "Współczucie i miłosierdzie",
        "boundaries_consent_privacy": "Granice, zgoda i prywatność",
        "dignity_and_respect": "Godność i szacunek",
        "stewardship": "Odpowiedzialne gospodarowanie",
    },
    "en": {
        "anger": "Anger and retaliation",
        "honesty": "Truth and honesty",
        "forgiveness": "Forgiveness and reconciliation",
        "conflict": "Conflict and reconciliation",
        "fear": "Fear and trust",
        "generosity": "Generosity and care",
        "prejudice": "Impartiality and love across divisions",
        "discernment": "Discernment of information",
        "grief": "Grief and comfort",
        "loneliness": "Loneliness and belonging",
        "repentance": "Repentance and making amends",
        "hope": "Hope and perseverance",
        "envy": "Envy and gratitude",
        "humility": "Pride and humility",
        "self_control": "Temptation and self-control",
        "justice": "Justice",
        "responsibility": "Responsibility",
        "compassion": "Compassion and mercy",
        "boundaries_consent_privacy": "Boundaries, consent, and privacy",
        "dignity_and_respect": "Dignity and respect",
        "stewardship": "Stewardship",
    },
}


THEME_NAMES = {
    "pl": {
        "anger": "gniewu oraz rezygnacji z odwetu",
        "honesty": "prawdy i uczciwości",
        "forgiveness": "przebaczenia i pojednania",
        "conflict": "rozwiązywania konfliktu",
        "fear": "lęku, zaufania i pokoju",
        "generosity": "hojności i troski o innych",
        "prejudice": "uprzedzeń, bezstronności i miłości do obcego",
        "discernment": "sprawdzania informacji przed wydaniem osądu",
        "grief": "żałoby, straty i pocieszenia",
        "loneliness": "samotności, obecności i przynależności",
        "repentance": "skruchy, naprawienia krzywdy i zmiany postępowania",
        "hope": "nadziei i wytrwałości w trudnościach",
        "envy": "zazdrości, wdzięczności i porównywania się",
        "humility": "pychy, pokory i gotowości do służby",
        "self_control": "pokusy, samokontroli i wolności od nałogu",
        "justice": "sprawiedliwości i uczciwego traktowania",
        "responsibility": "odpowiedzialności i dotrzymywania zobowiązań",
        "compassion": "współczucia, miłosierdzia i konkretnej pomocy",
        "boundaries_consent_privacy": "granic, świadomej zgody i prywatności",
        "dignity_and_respect": "godności człowieka i okazywania szacunku",
        "stewardship": "odpowiedzialnego gospodarowania środowiskiem i dobrami wspólnymi",
    },
    "en": {
        "anger": "anger and responding without retaliation",
        "honesty": "truth and honesty",
        "forgiveness": "forgiveness and reconciliation",
        "conflict": "handling conflict",
        "fear": "fear, trust, and peace",
        "generosity": "generosity and care for others",
        "prejudice": "prejudice, impartiality, and love for the stranger",
        "discernment": "checking claims before passing judgment",
        "grief": "grief, loss, and comfort",
        "loneliness": "loneliness, presence, and belonging",
        "repentance": "repentance, making amends, and changed conduct",
        "hope": "hope and perseverance in hardship",
        "envy": "envy, gratitude, and comparison",
        "humility": "pride, humility, and willingness to serve",
        "self_control": "temptation, self-control, and freedom from addiction",
        "justice": "justice and fair treatment",
        "responsibility": "responsibility and keeping commitments",
        "compassion": "compassion, mercy, and practical help",
        "boundaries_consent_privacy": "personal boundaries, informed consent, and privacy",
        "dignity_and_respect": "human dignity and respect for others",
        "stewardship": "responsible stewardship of the environment and common goods",
    },
}


def relevance_note(themes: tuple[str, ...], language: Language) -> str:
    names = [THEME_NAMES[language][theme] for theme in themes if theme in THEME_NAMES[language]]
    if language == "pl":
        if names:
            return f"Ten fragment odnosi się do tematu: {', '.join(names)}."
        return "Ten fragment został dopasowany znaczeniowo do opisanego dylematu."
    if names:
        return f"This passage addresses this theme: {', '.join(names)}."
    return "This passage was matched semantically to the dilemma you described."
