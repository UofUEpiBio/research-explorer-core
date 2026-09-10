# Changelog

## 0.2.0

- Adopt a flat `divisions` and `faculty` directory schema, with legacy snapshot
  normalization at the public boundary.
- Prevent title-only publication merges when either record has an identifier.
- Require a configured contact address before PubMed collection.
- Publish the `research-explorer-rag` command and verify built wheels in CI.
