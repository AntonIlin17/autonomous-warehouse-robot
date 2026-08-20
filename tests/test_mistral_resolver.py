"""Mocked Mistral success and failure-path tests."""

import json
from pathlib import Path

import pytest

from warehouse_robot_llm.location_registry import LocationRegistry
from warehouse_robot_llm.mistral_resolver import (
    HybridResolver,
    MistralMalformedResponseError,
    MistralResolver,
    MistralTimeoutError,
    MistralTransportError,
    MistralUnauthorizedError,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = LocationRegistry.from_csv(
    ROOT / "src" / "warehouse_robot_nav" / "config" / "locations.csv"
)


def envelope(location):
    content = json.dumps({"location": location})
    return json.dumps({"choices": [{"message": {"content": content}}]})


def resolver(transport):
    return MistralResolver(REGISTRY, api_key="test-only", transport=transport)


def test_mocked_success_resolves_non_keyword_phrase_to_charging():
    result = resolver(lambda *_: (200, envelope("charging_station"))).resolve(
        "the battery is almost dead"
    )
    assert result.destination_id == "charging_station"


def test_http_error_is_reported_without_response_body_leakage():
    with pytest.raises(MistralTransportError, match="HTTP 500"):
        resolver(lambda *_: (500, "sensitive upstream detail")).resolve("help")


def test_timeout_is_typed():
    def timeout(*_):
        raise TimeoutError("socket detail")

    with pytest.raises(MistralTimeoutError, match="timed out"):
        resolver(timeout).resolve("help")


def test_malformed_response_is_rejected():
    with pytest.raises(MistralMalformedResponseError):
        resolver(lambda *_: (200, "not json")).resolve("help")


def test_non_allow_list_destination_is_rejected():
    with pytest.raises(MistralMalformedResponseError, match="non-allow-listed"):
        resolver(lambda *_: (200, envelope("airport"))).resolve("go outside")


def test_unauthorized_is_typed():
    with pytest.raises(MistralUnauthorizedError, match="401"):
        resolver(lambda *_: (401, "credential rejected")).resolve("help")


def test_error_falls_back_to_deterministic_alias():
    hybrid = HybridResolver(REGISTRY, resolver(lambda *_: (503, "unavailable")))
    result = hybrid.resolve("go to the loading dock")
    assert result.location.destination_id == "loading_area"
    assert result.backend == "keyword_fallback"
    assert result.detail == "MistralTransportError"


def test_unauthorized_non_keyword_phrase_does_not_guess():
    hybrid = HybridResolver(REGISTRY, resolver(lambda *_: (401, "rejected")))
    result = hybrid.resolve("the battery is almost dead")
    assert result.location is None
    assert result.backend == "keyword_fallback"
