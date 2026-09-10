"""Stable records and adapter protocols shared by explorer applications."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Division:
    id: str
    name: str
    source_url: str
    faculty_url: str
    summary: str = ""


@dataclass(frozen=True)
class Faculty:
    id: str
    full_name: str
    profile_url: str
    division_ids: tuple[str, ...] = ()
    title: str = ""
    bio: str = ""
    academic_information: str = ""
    orcid_id: str = ""
    pubmed_query: str = ""
    arxiv_query: str = ""
    collect_publications: bool = True


@dataclass(frozen=True)
class Publication:
    id: str
    title: str
    faculty_ids: tuple[str, ...] = ()
    division_ids: tuple[str, ...] = ()
    doi: str = ""
    pmid: str = ""
    url: str = ""
    year: int = 0
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class HealthReport:
    source: str
    status: str
    message: str = ""
    checked_at: str = ""


@dataclass
class CollectionResult:
    status: str = "ok"
    message: str = ""
    items: list[dict] = field(default_factory=list)
    overview: str = ""


class DirectoryAdapter(Protocol):
    def collect_divisions(self) -> Sequence[Division]: ...

    def collect_faculty(self, division: Division) -> Sequence[Faculty]: ...


class ProfileAdapter(Protocol):
    def collect_profile(self, faculty: Faculty) -> Faculty: ...


class PublicationCollector(Protocol):
    def collect_publications(self, faculty: Faculty) -> Sequence[Publication]: ...


def collect_directory(
    directory_adapter: DirectoryAdapter, profile_adapter: ProfileAdapter | None = None
) -> dict[str, object]:
    """Collect a flat directory through the public adapter protocols.

    Applications can persist this result directly as ``directory.json`` and pass it to
    the works and retrieval builders. A profile adapter is optional because many
    directory pages already contain enough faculty metadata.
    """

    divisions = list(directory_adapter.collect_divisions())
    faculty_by_id: dict[str, Faculty] = {}
    for division in divisions:
        for member in directory_adapter.collect_faculty(division):
            enriched = profile_adapter.collect_profile(member) if profile_adapter else member
            existing = faculty_by_id.get(enriched.id)
            memberships = tuple(
                dict.fromkeys(
                    (
                        *((existing.division_ids) if existing else ()),
                        *enriched.division_ids,
                        division.id,
                    )
                )
            )
            faculty_by_id[enriched.id] = Faculty(
                **{**enriched.__dict__, "division_ids": memberships}
            )
    return {
        "schema_version": 1,
        "settings": {},
        "divisions": [division.__dict__ for division in divisions],
        "faculty": [faculty.__dict__ for faculty in faculty_by_id.values()],
    }


def normalize_directory(value: Mapping[str, object]) -> dict[str, object]:
    """Return the stable, flat directory shape used by collection and retrieval.

    ``organizations``/``researchers`` snapshots from pre-0.2 explorer sites remain
    accepted at this boundary only. New integrations should write ``divisions`` and
    ``faculty`` directly; no downstream component needs to know the legacy schema.
    """

    settings = dict(value.get("settings") or value.get("network") or {})
    if "divisions" in value or "faculty" in value:
        divisions = [dict(item) for item in value.get("divisions", []) if isinstance(item, Mapping)]
        faculty = [dict(item) for item in value.get("faculty", []) if isinstance(item, Mapping)]
    else:
        divisions = []
        faculty_by_id: dict[str, dict[str, object]] = {}
        for organization in value.get("organizations", []):
            if not isinstance(organization, Mapping) or not organization.get("id"):
                continue
            division_id = str(organization["id"])
            divisions.append(
                {
                    "id": division_id,
                    "name": str(organization.get("name", division_id)),
                    "source_url": str(organization.get("url", "")),
                    "faculty_url": str(organization.get("faculty_url", "")),
                    "summary": str(organization.get("summary", "")),
                }
            )
            for researcher in organization.get("researchers", []):
                if not isinstance(researcher, Mapping) or not researcher.get("id"):
                    continue
                faculty_id = str(researcher["id"])
                item = faculty_by_id.setdefault(
                    faculty_id,
                    {
                        "id": faculty_id,
                        "full_name": str(researcher.get("full_name", "")),
                        "profile_url": str(
                            researcher.get("profile_url", researcher.get("url", ""))
                        ),
                        "division_ids": [],
                        "title": str(researcher.get("title", researcher.get("role", ""))),
                        "bio": str(researcher.get("bio", "")),
                        "academic_information": str(researcher.get("academic_information", "")),
                        "orcid_id": str(researcher.get("orcid_id", "")),
                        "pubmed_query": str(researcher.get("pubmed_query", "")),
                        "arxiv_query": str(researcher.get("arxiv_query", "")),
                        "collect_publications": bool(researcher.get("collect_works", True)),
                    },
                )
                item["division_ids"] = list(dict.fromkeys([*item["division_ids"], division_id]))
        faculty = list(faculty_by_id.values())

    for item in faculty:
        item["division_ids"] = list(dict.fromkeys(item.get("division_ids", []) or []))
        item.setdefault("collect_publications", item.pop("collect_works", True))
    return {"schema_version": 1, "settings": settings, "divisions": divisions, "faculty": faculty}
