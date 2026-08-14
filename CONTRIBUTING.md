# Contributing

Use Python 3.11 or newer. Install the project locally and run `python -m unittest discover -s tests -v` before opening a pull request.

Contributions that add network access, command execution, providers, templates, or filesystem behavior must update tests and `docs/threat-model.md`. Providers may not accept endpoints or headers from lesson content.

For every contributed example, voice, font, image, template, or course asset, document its author, source URL, license, and redistribution permission. Do not contribute generated media whose provider terms prohibit redistribution.

Never commit credentials, `.env` files, authorization headers, private course libraries, or personal data.
