# Threat Model

## Assets

Provider credentials, local files, lesson content, generated media, release workflows, and downstream users are protected assets.

## Trust boundaries and threats

- Lesson and translation text may contain prompt injection, HTML, shell fragments, URLs, or filenames. It remains data and is schema-validated and escaped.
- Generated names may attempt path traversal or symlink escape. `OutputWorkspace` confines and owns writes.
- A provider contribution may exfiltrate credentials, perform SSRF-like requests, follow redirects, or return oversized/malicious content. Providers use trusted configuration, HTTPS, allowlists, timeouts, response limits, and maintainer review.
- Generated HTML may execute scripts or connect remotely. Only packaged templates are used; values are escaped and CSP disables scripts and connections.
- Dependency or GitHub Actions changes may introduce supply-chain code. CI actions are pinned, permissions are read-only, dependencies are audited, and sensitive paths require review.
- Agent Skills may interpret lesson text as commands. The Skill declares inputs untrusted and permits only six CLI subcommands.

## Residual risk

Third-party TTS services receive lesson text when explicitly enabled. Their terms, storage, jurisdiction, voice rights, and availability remain the user's responsibility. Windows reparse-point behavior requires ongoing cross-platform testing.
