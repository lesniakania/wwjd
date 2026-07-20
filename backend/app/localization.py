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


THEME_NAMES = {
    "pl": {
        "anger": "gniewu i reagowania bez odwetu",
        "honesty": "prawdy i uczciwości",
        "forgiveness": "przebaczenia i pojednania",
        "conflict": "rozwiązywania konfliktu",
        "fear": "lęku, zaufania i pokoju",
        "generosity": "hojności i troski o innych",
        "prejudice": "uprzedzeń, bezstronności i miłości do obcego",
        "discernment": "sprawdzania informacji przed wydaniem osądu",
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
