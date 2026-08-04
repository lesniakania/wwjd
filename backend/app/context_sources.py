import re

from .models import ContextSource
from .localization import Language, POLISH_BOOKS


VATICAN_CATECHISM_URL = (
    "https://www.vatican.va/archive/ENG0015/_INDEX.HTM"
)
OPEN_BIBLE_PERICOPE_URL = "https://www.openbible.info/labs/cross-references/"
BEREAN_DOWNLOADS_URL = "https://berean.bible/downloads.htm"
POLISH_CATECHISM_URL = "https://www.katechizm.opoka.org.pl/"
POLISH_BIBLE_URL = "https://www.bible.com/pl/bible/138"

BOOK_SLUGS = {
    "Genesis": "genesis", "Exodus": "exodus", "Leviticus": "leviticus",
    "Numbers": "numbers", "Deuteronomy": "deuteronomy", "Joshua": "joshua",
    "Judges": "judges", "Ruth": "ruth", "1 Samuel": "1samuel",
    "2 Samuel": "2samuel", "1 Kings": "1kings", "2 Kings": "2kings",
    "1 Chronicles": "1chronicles", "2 Chronicles": "2chronicles", "Ezra": "ezra",
    "Nehemiah": "nehemiah", "Tobit": "tobit", "Judith": "judith",
    "Esther": "esther", "1 Maccabees": "1maccabees", "2 Maccabees": "2maccabees",
    "Job": "job", "Psalms": "psalms", "Psalm": "psalms", "Proverbs": "proverbs",
    "Ecclesiastes": "ecclesiastes", "Song of Solomon": "songofsongs", "Wisdom": "wisdom",
    "Sirach": "sirach", "Isaiah": "isaiah", "Jeremiah": "jeremiah",
    "Lamentations": "lamentations", "Baruch": "baruch", "Ezekiel": "ezekiel",
    "Daniel": "daniel", "Hosea": "hosea", "Joel": "joel", "Amos": "amos",
    "Obadiah": "obadiah", "Jonah": "jonah", "Micah": "micah", "Nahum": "nahum",
    "Habakkuk": "habakkuk", "Zephaniah": "zephaniah", "Haggai": "haggai",
    "Zechariah": "zechariah", "Malachi": "malachi", "Matthew": "matthew",
    "Mark": "mark", "Luke": "luke", "John": "john", "Acts": "acts",
    "Romans": "romans", "1 Corinthians": "1corinthians", "2 Corinthians": "2corinthians",
    "Galatians": "galatians", "Ephesians": "ephesians", "Philippians": "philippians",
    "Colossians": "colossians", "1 Thessalonians": "1thessalonians",
    "2 Thessalonians": "2thessalonians", "1 Timothy": "1timothy",
    "2 Timothy": "2timothy", "Titus": "titus", "Philemon": "philemon",
    "Hebrews": "hebrews", "James": "james", "1 Peter": "1peter",
    "2 Peter": "2peter", "1 John": "1john", "2 John": "2john", "3 John": "3john",
    "Jude": "jude", "Revelation": "revelation",
}

BOOK_PATTERN = "|".join(sorted((re.escape(book) for book in BOOK_SLUGS), key=len, reverse=True))
SCRIPTURE_PATTERN = re.compile(rf"^(?P<book>{BOOK_PATTERN}) (?P<chapter>\d+)(?::|$)")
USCCB_PATTERN = re.compile(
    rf"^USCCB, (?:(?:Introduction to )?)(?P<book>{BOOK_PATTERN})(?: (?P<chapter>\d+))?"
)

BIBLE_COM_BOOK_CODES = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM",
    "Deuteronomy": "DEU", "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT",
    "1 Samuel": "1SA", "2 Samuel": "2SA", "1 Kings": "1KI", "2 Kings": "2KI",
    "1 Chronicles": "1CH", "2 Chronicles": "2CH", "Ezra": "EZR",
    "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
    "Psalm": "PSA", "Proverbs": "PRO", "Ecclesiastes": "ECC",
    "Song of Solomon": "SNG", "Isaiah": "ISA", "Jeremiah": "JER",
    "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN", "Hosea": "HOS",
    "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
    "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP",
    "Haggai": "HAG", "Zechariah": "ZEC", "Malachi": "MAL", "Matthew": "MAT",
    "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT", "Romans": "ROM",
    "1 Corinthians": "1CO", "2 Corinthians": "2CO", "Galatians": "GAL",
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
    "1 Thessalonians": "1TH", "2 Thessalonians": "2TH", "1 Timothy": "1TI",
    "2 Timothy": "2TI", "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB",
    "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE", "1 John": "1JN",
    "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV",
}


def _usccb_bible_url(book: str, chapter: str | None) -> str:
    return f"https://bible.usccb.org/bible/{BOOK_SLUGS[book]}/{chapter or '0'}"


def _polish_scripture_source(label: str, match: re.Match[str]) -> ContextSource:
    book = match.group("book")
    chapter = match.groupdict().get("chapter")
    book_name = POLISH_BOOKS.get(book, book)
    reference_suffix = label[match.end("book"):]
    if label.startswith("USCCB"):
        localized_label = f"{book_name}{f' {chapter}' if chapter else ''} — tekst biblijny (UBG)"
    else:
        localized_label = f"{book_name}{reference_suffix} (UBG)"
    book_code = BIBLE_COM_BOOK_CODES.get(book)
    url = (
        f"{POLISH_BIBLE_URL}/{book_code}.{chapter}.UBG"
        if book_code and chapter
        else POLISH_BIBLE_URL
    )
    return ContextSource(label=localized_label, url=url)


def context_source(label: str, language: Language = "en") -> ContextSource:
    if label.startswith("Catechism of the Catholic Church"):
        if language == "pl":
            suffix = label.removeprefix("Catechism of the Catholic Church")
            return ContextSource(
                label=f"Katechizm Kościoła Katolickiego{suffix}",
                url=POLISH_CATECHISM_URL,
            )
        return ContextSource(label=label, url=VATICAN_CATECHISM_URL)
    if label.startswith("OpenBible.info"):
        return ContextSource(label=label, url=OPEN_BIBLE_PERICOPE_URL)
    if label.startswith("Berean Standard Bible"):
        return ContextSource(label=label, url=BEREAN_DOWNLOADS_URL)

    match = USCCB_PATTERN.match(label) or SCRIPTURE_PATTERN.match(label)
    if match:
        if language == "pl":
            return _polish_scripture_source(label, match)
        return ContextSource(
            label=label,
            url=_usccb_bible_url(match.group("book"), match.groupdict().get("chapter")),
        )
    raise ValueError(f"Unsupported context source: {label}")
