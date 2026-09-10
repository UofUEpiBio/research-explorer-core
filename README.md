# Research Explorer Core

Reusable Python primitives for public research and faculty explorer sites.

The package deliberately contains no institution-specific URLs, HTML selectors, branding,
web server, or cloud deployment policy. Applications supply those concerns through the
adapter protocols in `research_explorer.models`.

## Included components

- typed directory and publication records plus adapter protocols;
- respectful HTTP collection with retries, rate limiting, and robots checks;
- public scholarly metadata collection and identifier-first deduplication; and
- deterministic text, retrieval-index, and hybrid-search utilities.

## Directory contract

The canonical input is a flat `directory.json` with `divisions` and `faculty` arrays.
Faculty records use `division_ids`; publication records use `faculty_ids` and
`division_ids`. `normalize_directory()` accepts older nested snapshots at the boundary
to support staged migrations, but new applications should use the flat contract.

Implement `DirectoryAdapter` (and optionally `ProfileAdapter`) then call
`collect_directory()` to produce a directory snapshot. The package deliberately does
not prescribe HTML selectors or a scraping framework.

## Operations

Build a retrieval index from published snapshots:

```sh
research-explorer-rag --directory data/directory.json --publications data/publications.json
```

Set `RESEARCH_EXPLORER_CONTACT_EMAIL` to a real monitored address before PubMed
collection. Optionally set `RESEARCH_EXPLORER_NCBI_TOOL` and `NCBI_API_KEY`; the library
will never send a placeholder email address to NCBI.

## Development

```sh
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The first consumer is [DOIM Explorer](https://github.com/UofUEpiBio/doim-explorer).
