# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Use GitHub's private
vulnerability reporting: **Security → Report a vulnerability** on this repository.

Include what you found, which file or document is affected, and (if relevant) how to reproduce it.

## Scope

- Code in `src/tgkit/` and `examples/`.
- Documentation that gives security advice which is wrong or unsafe.

## What this repository never contains

Real bot tokens, webhook secrets, or user data. If you find one in the history, report it
privately so it can be revoked and removed.

## If your own bot token leaked

See [docs/05-security/02-token-leak-response.md](docs/05-security/02-token-leak-response.md).
