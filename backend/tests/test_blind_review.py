from app.blind_review import build_case


def test_pool_deduplicates_localized_references_and_hides_provenance() -> None:
    case = {"id": "case", "situation": "Test", "category": "test",
            "expected_sources": [{"reference": "Luke 10:27"}]}
    source = {"reference": "Łukasza 10:27", "quotation": "text",
              "situation_application": "Application"}
    packet, key = build_case(case, {"baseline": [source], "reranker": [source]},
                             {("Luke", 10, 27): "text"})
    assert len(packet["passages"]) == 1
    assert len(packet["applications"]) == 1
    assert packet["passages"][0]["rating"] is None
    assert "baseline" not in str(packet)
    assert set(next(iter(key["passages"].values()))) == {"gold", "baseline", "reranker"}
