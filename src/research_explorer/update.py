"""Small, application-neutral command helpers for retrieval-index maintenance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_explorer import rag


def parse_rag_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild a research-explorer retrieval index")
    parser.add_argument(
        "--directory", "--profiles", dest="directory", default="data/directory.json"
    )
    parser.add_argument(
        "--publications", "--works", dest="publications", default="data/publications.json"
    )
    parser.add_argument("--details", default="")
    parser.add_argument("--output-dir", default="data/rag")
    parser.add_argument("--dims", type=int, default=rag.DEFAULT_DIMS)
    parser.add_argument("--model", default=rag.DEFAULT_MODEL)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-embed", action="store_true")
    return parser.parse_args(argv)


def _read_json(path: str) -> dict | None:
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def rag_main(argv: list[str] | None = None) -> int:
    args = parse_rag_args(argv)
    directory = _read_json(args.directory)
    works = _read_json(args.publications)
    if directory is None or works is None:
        print(f"Missing {args.directory} or {args.publications}")
        return 1

    details_path = args.details or str(
        Path(args.publications).with_name("publications-details.json")
    )
    details = _read_json(details_path) or {"details": {}}
    chunks = rag.build_chunks(directory, works, details)
    previous = None if args.replace else rag.read_index(args.output_dir)
    if args.dry_run:
        known = {chunk["id"]: chunk["hash"] for chunk in previous.chunks} if previous else {}
        stale = sum(1 for chunk in chunks if known.get(chunk["id"]) != chunk["hash"])
        print(f"{len(chunks)} chunks: {stale} would be embedded, {len(chunks) - stale} reused")
        return 0

    if args.no_embed:
        result = rag.BuildResult(chunks=chunks, vectors={}, dims=args.dims, model=args.model)
    else:
        embedder = rag.vertex_embedder(model=args.model, dims=args.dims)
        result = rag.build_index(chunks, previous, embedder, dims=args.dims, model=args.model)
    rag.write_index(result, args.output_dir)
    return 0
