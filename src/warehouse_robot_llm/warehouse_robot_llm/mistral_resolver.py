"""Mistral-backed destination resolver with strict allow-list enforcement."""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from .location_registry import Location, LocationRegistry

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_TIMEOUT_SECONDS = 8.0


class MistralResolutionError(RuntimeError):
    """Base class for safe-to-report resolver failures."""


class MistralUnauthorizedError(MistralResolutionError):
    """The Mistral credential was rejected."""


class MistralTimeoutError(MistralResolutionError):
    """The Mistral request exceeded its timeout."""


class MistralMalformedResponseError(MistralResolutionError):
    """The service response did not match the expected schema."""


class MistralTransportError(MistralResolutionError):
    """The Mistral request failed before a valid result was available."""


Transport = Callable[[dict, dict, float], tuple[int, str]]


@dataclass(frozen=True)
class Resolution:
    """The selected destination and the backend that selected it."""

    location: Location | None
    backend: str
    detail: str = ""


def _http_transport(payload: dict, headers: dict, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(
        MISTRAL_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except (TimeoutError, socket.timeout) as exc:
        raise MistralTimeoutError("Mistral request timed out") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            raise MistralTimeoutError("Mistral request timed out") from exc
        raise MistralTransportError("Mistral network request failed") from exc


class MistralResolver:
    """Resolve free-form intent while accepting only configured locations."""

    def __init__(
        self,
        registry: LocationRegistry,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        transport: Transport | None = None,
    ):
        self.registry = registry
        self.api_key = (api_key if api_key is not None else os.getenv("MISTRAL_API_KEY", "")).strip()
        self.model = model
        self.timeout = timeout
        self.transport = transport or _http_transport

    def _system_prompt(self) -> str:
        catalog = "\n".join(
            f"- {location.destination_id}: {location.description}"
            for location in self.registry.all()
        )
        allowed = ", ".join(location.destination_id for location in self.registry.all())
        return (
            "Select exactly one destination for a warehouse robot.\n"
            f"Destinations:\n{catalog}\n"
            "Return JSON only: {\"location\": \"<id or none>\"}.\n"
            f"The location must be one of: {allowed}, none. Do not invent destinations."
        )

    def resolve(self, command: str) -> Location | None:
        """Call Mistral and validate its answer against the registry."""
        if not command.strip():
            return None
        if not self.api_key:
            raise MistralUnauthorizedError("MISTRAL_API_KEY is not set")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": command},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "max_tokens": 80,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            status, body = self.transport(payload, headers, self.timeout)
        except MistralResolutionError:
            raise
        except (TimeoutError, socket.timeout) as exc:
            raise MistralTimeoutError("Mistral request timed out") from exc
        except Exception as exc:
            raise MistralTransportError("Mistral request failed") from exc

        if status in (401, 403):
            raise MistralUnauthorizedError(f"Mistral rejected the credential ({status})")
        if status != 200:
            raise MistralTransportError(f"Mistral returned HTTP {status}")

        try:
            envelope = json.loads(body)
            content = envelope["choices"][0]["message"]["content"]
            parsed = json.loads(content) if isinstance(content, str) else content
            candidate = str(parsed["location"])
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise MistralMalformedResponseError("Mistral response was malformed") from exc

        if candidate.strip().lower() == "none":
            return None
        location = self.registry.canonicalize(candidate)
        if location is None:
            raise MistralMalformedResponseError("Mistral returned a non-allow-listed destination")
        return location


class HybridResolver:
    """Use Mistral first and deterministic aliases as the safe fallback."""

    def __init__(self, registry: LocationRegistry, mistral: MistralResolver):
        self.registry = registry
        self.mistral = mistral

    def resolve(self, command: str) -> Resolution:
        """Resolve with Mistral, falling back after errors or an undecided response."""
        if not command.strip():
            return Resolution(None, "none")
        try:
            location = self.mistral.resolve(command)
            if location:
                return Resolution(location, "mistral")
            return Resolution(self.registry.match(command), "keyword_fallback", "no_mistral_match")
        except MistralResolutionError as exc:
            fallback = self.registry.match(command)
            return Resolution(fallback, "keyword_fallback", type(exc).__name__)
