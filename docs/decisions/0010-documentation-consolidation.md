# Decision: Consolidate Current Documentation into Five Guides

## Context

Topic-specific subdirectories duplicated setup, operation, test, and internal
processing descriptions. Readers could not easily tell which file contained the
current specification.

## Decision

1. Keep the current documentation in five chapter-numbered files under
   **docs/**: **SETUP.md**, **TUTORIAL.md**, **SYNTAX_BINDING.md**,
   **SEMANTIC_BINDING.md**, and **DATA_MODEL.md**.
2. Include operating procedures and function-level implementation detail in the
   relevant guide instead of maintaining a separate script-processing manual.
3. Keep **docs/decisions/** as historical architecture rationale.
4. Place a short **README.md** in each script-oriented directory so GitHub users
   can understand its contents without first navigating to **docs/**.
5. Treat Markdown as source and regenerate PDFs for a synchronized release.

## Consequences

- The five guides are the only current normative human-readable documentation.
- Old duplicated guide directories are removed after their unique content is
  migrated.
- Script behavior changes update the applicable guide and directory README in
  the same change.
- Architecture records remain concise and refer to current guides rather than
  restating their implementation details.
