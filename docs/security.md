# Security Controls

- Strict models reject unknown fields and unsafe identifiers.
- Safe YAML loading rejects executable tags.
- Output paths reject traversal, drive changes, UNC paths, null bytes, and symbolic-link escape.
- Templates are packaged, sandboxed, escaped, and offline under CSP.
- HTTP TTS requires HTTPS, optional host allowlisting, timeouts, MIME validation, and a 10 MiB response limit.
- Credentials come from one named environment variable and are excluded from errors and manifests.
