# Choosing a Library

> **TL;DR:** python-telegram-bot has the largest community and the most stars; aiogram is the strongest alternative in Python; grammY is the healthiest choice in TypeScript; Telegraf is mature but its last release was in February 2024. All of them wrap the same Bot API.
> **Applies to:** data as of 2026-11-26 · Last verified 2026-11-26

## 1. Numbers (GitHub stars, latest release)

| Library | Language | Stars | Latest release | License |
| :--- | :--- | ---: | :--- | :--- |
| **python-telegram-bot** | Python | 29.6k | 22.8 (2026-06-12) | LGPL-3.0 |
| pyTelegramBotAPI | Python | 8.8k | 4.37.0 (2026-09-21) | GPL-2.0 |
| aiogram | Python | 5.9k | 3.34.0 (2026-11-22) | MIT |
| node-telegram-bot-api | JavaScript | 9.2k | 2.4.x | MIT |
| Telegraf | TypeScript | 9.2k | 4.16.3 (2024-02-29) | MIT |
| grammY | TypeScript | 3.8k | 1.48.0 (2026-11-22) | MIT |
| Telegram.Bots | Java | 5.6k | active | MIT |
| telego | Go | 1.1k | active | MIT |

Stars are a popularity signal, not a quality score. Check the release date and whether the library tracks the current Bot API.

## 2. The Python choice

| Need | Pick |
| :--- | :--- |
| Biggest community, most examples, batteries included | **python-telegram-bot** |
| Routers, middlewares, FSM, aiohttp-native | aiogram |
| Very small bots, synchronous style | pyTelegramBotAPI |

python-telegram-bot 22.8 natively supports Bot API 10.0. aiogram 3.34 tracks the API closely too. Neither is at 10.5 yet, so both need raw calls for the newest methods.

## 3. The TypeScript choice

| Need | Pick |
| :--- | :--- |
| Actively maintained, plugins, serverless support | **grammY** |
| Existing Telegraf codebase | Telegraf (note: no release since Feb 2024) |
| Thin wrapper, one function per method | node-telegram-bot-api |

grammY ships adapters for Node, Deno and serverless platforms, which matters if you want webhooks on edge runtimes.

## 4. Framework vs wrapper

| Kind | Examples | You get |
| :--- | :--- | :--- |
| Framework | python-telegram-bot, aiogram, grammY, Telegraf | routing, middleware, state, keyboards |
| Wrapper | node-telegram-bot-api, telego (thin mode) | one function per API method |

Frameworks save time; wrappers give control. Most production bots are better off with a framework.

## 5. Questions that decide it

1. **Which language is your team fluent in?** This dominates everything else.
2. **Does the library track new Bot API versions?** Check the changelog and the `__bot_api_version__`.
3. **Is it maintained?** Last release within ~12 months.
4. **Does it support your deployment?** Polling, webhook, serverless.
5. **What is the licence?** LGPL/GPL matter if you redistribute.

## 6. What this handbook uses

**python-telegram-bot 22.8**, because it is the most starred Telegram library, has the most examples and documentation, and every concept in this handbook maps to it. Most chapters also apply to aiogram and grammY with different names.

## Sources

- https://github.com/python-telegram-bot/python-telegram-bot
- https://github.com/aiogram/aiogram
- https://github.com/eternnoir/pyTelegramBotAPI
- https://github.com/grammyjs/grammY
- https://github.com/telegraf/telegraf
- https://github.com/yagop/node-telegram-bot-api
- https://core.telegram.org/bots/samples
