"""Load and validate the project's canonical named-location configuration."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


def normalize_text(text: str) -> str:
    """Return lowercase words separated by single spaces."""
    normalized = text.lower().replace("_", " ")
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


@dataclass(frozen=True)
class Location:
    """One allow-listed warehouse destination."""

    destination_id: str
    name: str
    x: float
    y: float
    yaw: float
    aliases: tuple[str, ...]
    description: str


class LocationRegistry:
    """Validated destinations and longest-first alias matching."""

    def __init__(self, locations: list[Location]):
        if not locations:
            raise ValueError("At least one location is required")

        self._locations = {location.destination_id: location for location in locations}
        if len(self._locations) != len(locations):
            raise ValueError("Destination IDs must be unique")

        aliases: list[tuple[str, str]] = []
        seen: dict[str, str] = {}
        for location in locations:
            candidates = (location.destination_id, location.name, *location.aliases)
            for candidate in candidates:
                normalized = normalize_text(candidate)
                if not normalized:
                    continue
                previous = seen.get(normalized)
                if previous and previous != location.destination_id:
                    raise ValueError(f"Alias {candidate!r} is assigned to multiple locations")
                seen[normalized] = location.destination_id
                aliases.append((normalized, location.destination_id))
        self._aliases = sorted(set(aliases), key=lambda item: len(item[0]), reverse=True)

    @classmethod
    def from_csv(cls, path: str | Path) -> "LocationRegistry":
        """Read locations from the canonical CSV file."""
        csv_path = Path(path)
        with csv_path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))

        expected = {"id", "name", "x", "y", "yaw", "aliases", "description"}
        if not rows or set(rows[0]) != expected:
            raise ValueError(f"Unexpected location columns in {csv_path}")

        locations = []
        for row in rows:
            destination_id = row["id"].strip()
            if not re.fullmatch(r"[a-z][a-z0-9_]*", destination_id):
                raise ValueError(f"Invalid destination ID: {destination_id!r}")
            locations.append(
                Location(
                    destination_id=destination_id,
                    name=row["name"].strip(),
                    x=float(row["x"]),
                    y=float(row["y"]),
                    yaw=float(row["yaw"]),
                    aliases=tuple(
                        alias.strip() for alias in row["aliases"].split(";") if alias.strip()
                    ),
                    description=row["description"].strip(),
                )
            )
        return cls(locations)

    def get(self, destination_id: str) -> Location:
        """Return an allow-listed location by ID."""
        return self._locations[destination_id]

    def all(self) -> tuple[Location, ...]:
        """Return all locations in configuration order."""
        return tuple(self._locations.values())

    def match(self, command: str) -> Location | None:
        """Resolve an explicit name or alias using word boundaries."""
        normalized = normalize_text(command)
        if not normalized:
            return None
        padded = f" {normalized} "
        for alias, destination_id in self._aliases:
            if f" {alias} " in padded:
                return self._locations[destination_id]
        return None

    def canonicalize(self, candidate: str) -> Location | None:
        """Accept only an exact configured ID, name, or alias."""
        normalized = normalize_text(candidate)
        for alias, destination_id in self._aliases:
            if normalized == alias:
                return self._locations[destination_id]
        return None
