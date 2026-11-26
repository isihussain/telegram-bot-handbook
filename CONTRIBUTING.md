# Contributing

Thanks for helping. This handbook only stays useful if every claim in it is correct and current.

## Ground rules

1. **Cite the source.** Every limit, parameter name or behaviour must come from the official
   docs (core.telegram.org/bots/api, /bots/faq, /bots/webhooks, /bots/webapps, /bots/payments-stars,
   the Bot API changelog) or from the library source. Put the links in the doc's `Sources` section.
2. **No unverified numbers.** If you are not sure, say "see the official docs" instead of guessing.
3. **Code must run.** Python blocks in docs must parse (`python scripts/check_docs.py`). Anything
   non-trivial belongs in `src/tgkit/` or `examples/` with a test.
4. **Defensive content only.** Explain how to protect bots and users. No spam tooling, no scrapers
   for private data, no guidance for evading Telegram's limits or bans.
5. **Never commit secrets.** Use placeholders like `123456:ABC-DEF...`.

## Doc template

Copy `docs/_TEMPLATE.md`. Required: H1 title, a `TL;DR` line, an `Applies to` line with the
Bot API and library versions and the verification date, and a `Sources` section.

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate   # Python 3.11+
make install          # pip install -e ".[dev]"
make check            # lint + docs + tests
```

`make` is a shortcut for the commands CI runs; run them directly if you prefer:

```bash
ruff check .
python scripts/check_docs.py          # allows links to pages listed in llms.txt
python scripts/check_docs.py --strict # every linked file must exist (run before a release)
pytest
```

Other targets: `make docs`, `make docs-strict`, `make test`, `make run` and `make clean`.
Run `make` with no arguments to list them.

## Pull requests

- One topic per PR. Link the issue it closes.
- CI must pass (lint, doc check, tests on Python 3.11 / 3.12 / 3.13).
- If a Bot API version changes behaviour, update the `Applies to` line and `docs/01-foundations/01-bot-api-overview.md`.
