# Glossary

> **TL;DR:** The vocabulary you need to read the Bot API docs and this handbook without guessing.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

| Term | Meaning |
| :--- | :--- |
| **Update** | JSON object describing something that happened; the unit of delivery |
| **`update_id`** | increasing identifier for an update; use it for de-duplication |
| **Method** | an API call such as `sendMessage` |
| **`chat_id`** | numeric id of a chat; positive for users, negative for groups/channels |
| **`user_id`** | numeric id of a user; never reuse usernames as identity |
| **`file_id`** | opaque, persistent reference to a file for **your** bot |
| **`file_unique_id`** | stable file identifier across bots |
| **Polling** | repeatedly calling `getUpdates` |
| **Webhook** | Telegram POSTs updates to your HTTPS endpoint |
| **`allowed_updates`** | the update types you subscribe to |
| **Privacy mode** | group setting that limits which messages a bot receives |
| **Inline mode** | `@bot query` results chosen by the user |
| **Callback query** | a press on an inline keyboard button |
| **Mini App** | a web app opened inside Telegram |
| **`initData`** | signed payload proving who opened a Mini App |
| **Stars (XTR)** | Telegram's currency for digital goods |
| **`telegram_payment_charge_id`** | unique payment id, needed for refunds |
| **Rich message** | structured message format introduced in Bot API 10.1 |
| **Ephemeral message** | group message visible only to one user |
| **Draft** | temporary streamed preview from `sendMessageDraft` |
| **Guest bot** | bot that can reply in chats it has not joined (Bot API 10.0) |
| **Community** | several chats linked around a topic (Bot API 10.2) |
| **Guard bot** | bot that handles join requests, optionally with a Mini App |
| **`retry_after`** | seconds to wait after a 429 |
| **Local Bot API server** | self-hosted `telegram-bot-api` with higher limits |
| **LGPL** | the licence of python-telegram-bot; matters if you redistribute |

## Sources

- https://core.telegram.org/bots/api
- https://core.telegram.org/bots/api-changelog
- https://core.telegram.org/bots/features
- https://core.telegram.org/bots/webapps
