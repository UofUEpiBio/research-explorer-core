"""Stable records and adapter protocols shared by explorer applications."""

from __future__ import annotations

from collections.abc import Sequence
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
