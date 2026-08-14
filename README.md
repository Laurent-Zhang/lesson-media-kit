# Lesson Media Kit

Lesson Media Kit is an early-stage, local-first Python CLI for turning structured language lessons into deterministic placeholder audio, SRT/VTT subtitles, trusted offline HTML scenes, and SHA-256 manifests.

It is intended for language teachers, curriculum developers, educational content creators, and maintainers building reproducible lesson-media pipelines. It has no adoption, stability, or download claims yet.

## Offline quick start

```bash
python -m venv .venv
python -m pip install -e .
lesson-media validate examples/basic-lesson/lesson.yaml
lesson-media build examples/basic-lesson/lesson.yaml --output build/example --provider dummy
```

The dummy provider performs no network access and creates deterministic silent WAV files. A build also creates `subtitles/lesson.srt`, `subtitles/lesson.vtt`, `scenes/lesson.html`, and `manifest.json`.

## Security posture

Lesson content and provider responses are untrusted data. Generated paths are confined to an explicit output directory, unowned files are never force-overwritten, templates are packaged and escaped, and the default provider is offline. See [the threat model](docs/threat-model.md) and [security policy](SECURITY.md).

## Non-goals

This project does not upload or publish media, automate browsers, execute arbitrary shell commands, load user templates, manage accounts, or include a production lesson library.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Security-sensitive changes to providers, Agent Skills, workflows, packaging, or the threat model require maintainer review.

Licensed under Apache-2.0.
