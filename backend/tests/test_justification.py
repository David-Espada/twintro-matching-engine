import pytest
from app.services.justification.justification_service import JustificationService


def test_failed_provider_falls_back_without_changing_scores(engine, engineer, product):
    class BrokenProvider:
        name = "broken"

        def explain(self, result):
            result.affinity_percentage = 1
            raise RuntimeError("Provider unavailable")

    result = engine.compare(engineer, product)
    before = result.affinity_percentage
    JustificationService(BrokenProvider()).apply(result)
    assert result.affinity_percentage == before
    assert result.metadata.justification_provider == "template"
    assert "Alex Rivera" in result.justification


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_empty_provider_response_falls_back(engine, engineer, product, empty):
    class EmptyProvider:
        name = "empty"

        def explain(self, result):
            return empty

    result = engine.compare(engineer, product)
    JustificationService(EmptyProvider()).apply(result)
    assert result.metadata.justification_provider == "template"
    assert result.justification.strip()
