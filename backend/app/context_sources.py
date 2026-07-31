import re

from .models import ContextSource


VATICAN_CATECHISM_URL = (
    "https://www.vatican.va/archive/ENG0015/_INDEX.HTM"
)
OPEN_BIBLE_PERICOPE_URL = "https://www.openbible.info/labs/cross-references/"
BEREAN_DOWNLOADS_URL = "https://berean.bible/downloads.htm"

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


def _usccb_bible_url(book: str, chapter: str | None) -> str:
    return f"https://bible.usccb.org/bible/{BOOK_SLUGS[book]}/{chapter or '0'}"


def context_source(label: str) -> ContextSource:
    if label.startswith("Catechism of the Catholic Church"):
        return ContextSource(label=label, url=VATICAN_CATECHISM_URL)
    if label.startswith("OpenBible.info"):
        return ContextSource(label=label, url=OPEN_BIBLE_PERICOPE_URL)
    if label.startswith("Berean Standard Bible"):
        return ContextSource(label=label, url=BEREAN_DOWNLOADS_URL)

    match = USCCB_PATTERN.match(label) or SCRIPTURE_PATTERN.match(label)
    if match:
        return ContextSource(
            label=label,
            url=_usccb_bible_url(match.group("book"), match.groupdict().get("chapter")),
        )
    raise ValueError(f"Unsupported context source: {label}")
