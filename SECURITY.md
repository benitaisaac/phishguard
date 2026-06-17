# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |

## Reporting a Vulnerability

If you discover a security issue, **please do not open a public issue**. Instead email
**aashish@marketdoctorsonline.com** with:

- a description of the vulnerability,
- steps to reproduce, and
- the potential impact.

You'll receive an acknowledgement within a few days and an estimated fix timeline.

## Security posture of this project

PhishGuard is designed to be safe by construction:

- **No backend, no database, no accounts** — the web dashboard runs entirely in the browser.
- **No data leaves the device** — URLs are analyzed locally; nothing is uploaded.
- **No secrets** — there are no API keys or credentials in this repository.
  `.env.example` documents the (optional) configuration surface only.
- **XSS-safe rendering** — all user-supplied values are HTML-escaped before insertion
  into the DOM, and user input is validated (`new URL(...)`).
- **No `eval`/`innerHTML` of untrusted input**, no third-party runtime dependencies.

> PhishGuard is an educational/research tool. It provides a probabilistic assessment and
> is **not** a guarantee of safety. Always verify suspicious links through official channels.
