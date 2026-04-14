
### Rust Core Rewrite (TODO)
**Future Goal:** To maximize efficiency, performance, and security, a major milestone on our roadmap is to rewrite the core parsing engine (`missing_text/extract`) in Rust using PyO3 bindings. This will allow the Python library to serve purely as a lightweight orchestrator while pushing CPU-intensive extraction operations (especially async IO, large byte handling, and concurrent layout analysis) to a safe, highly performant lower-level layer.
