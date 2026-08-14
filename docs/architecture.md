# Architecture

All JSON/YAML input becomes one strict `Lesson` model. Pure generators consume that model. `OutputWorkspace` confines writes and tracks generated-file ownership. `TTSProvider` separates offline and optional network behavior. `build_lesson` calls Python functions in a fixed order and never invokes a shell.
