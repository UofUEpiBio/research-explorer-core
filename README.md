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

## Development

```sh
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
```

The first consumer is [DOIM Explorer](https://github.com/UofUEpiBio/doim-explorer).
