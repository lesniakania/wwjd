"""Create human review packets without revealing candidate provenance."""

import hashlib

from .evaluation import parse_reference


def canonical_reference(reference: str) -> str:
    verses = sorted(parse_reference(reference))
    book, chapter, start = verses[0]
    end = verses[-1][2]
    return f"{book} {chapter}:{start}" + (f"-{end}" if start != end else "")


def build_case(
    case: dict, outputs: dict[str, list[dict]], corpus: dict[tuple[str, int, int], str],
) -> tuple[dict, dict]:
    origins: dict[str, list[str]] = {}
    applications: dict[tuple[str, str], list[str]] = {}
    for origin, sources in {"gold": case["expected_sources"], **outputs}.items():
        for source in sources:
            reference = canonical_reference(source["reference"])
            origins.setdefault(reference, []).append(origin)
            application = source.get("situation_application", "")
            if application:
                applications.setdefault((reference, application), []).append(origin)
    references = sorted(origins, key=lambda ref: hashlib.sha256(
        f"review-v1:{case['id']}:{ref}".encode()).hexdigest())
    passages = []
    passage_key = {}
    ids = {}
    for index, reference in enumerate(references, 1):
        identifier = f"{case['id']}-p{index:02}"
        ids[reference] = identifier
        verses = sorted(parse_reference(reference))
        book, chapter, start = verses[0]
        end = verses[-1][2]
        context = " ".join(f"[{verse}] {corpus[book, chapter, verse]}"
                           for verse in range(max(1, start - 3), end + 4)
                           if (book, chapter, verse) in corpus)
        passages.append({"id": identifier, "reference": reference,
                         "quotation": " ".join(corpus[verse] for verse in verses),
                         "surrounding_text": context, "rating": None, "notes": ""})
        passage_key[identifier] = sorted(set(origins[reference]))
    application_rows = []
    application_key = {}
    ordered = sorted(applications, key=lambda item: hashlib.sha256(
        f"review-v1:{case['id']}:{item}".encode()).hexdigest())
    for index, (reference, application) in enumerate(ordered, 1):
        identifier = f"{case['id']}-a{index:02}"
        application_rows.append({"id": identifier, "passage_id": ids[reference],
                                 "text": application, "rating": None, "notes": ""})
        application_key[identifier] = sorted(set(applications[reference, application]))
    return ({"id": case["id"], "category": case["category"], "situation": case["situation"],
             "passages": passages, "applications": application_rows},
            {"passages": passage_key, "applications": application_key})
