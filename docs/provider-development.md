# Provider Development

Implement `TTSProvider.synthesize(TTSRequest) -> TTSResult`. Provider endpoints, credential variable names, and headers come from trusted configuration, never lesson data. Require HTTPS, bound time and response size, validate media type, redact errors, expose only non-secret metadata, and add offline tests for failure branches. Update the threat model for every new network or execution capability.
