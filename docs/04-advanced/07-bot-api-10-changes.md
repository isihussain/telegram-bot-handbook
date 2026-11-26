# Bot API 10.x: What Changed in 2026

> **TL;DR:** 2026 brought rich messages, ephemeral messages, communities, guest bots, widgets, managed bots, private-chat topics, streaming drafts, checklists and TON wallet surfaces. python-telegram-bot 22.8 wraps the 10.0 surface; newer calls go through `do_api_request`.
> **Applies to:** Bot API 10.0–10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Timeline

| Version | Date | Headline features |
| :--- | :--- | :--- |
| **10.0** | 2026-05-08 | Guest mode, live photos, poll media, chat management additions, bot-to-bot messaging |
| **10.1** | 2026-06-11 | **Rich messages**, join request queries, poll links |
| **10.2** | 2026-07-14 | Rich message blocks/media, **ephemeral messages**, communities, subscription updates, Mini App origin hardening |
| **10.3** | 2026-08-24 | Rich message buttons, more blocks, ephemeral editing, disabled buttons, `sendMessageDraft` stop controls |
| **10.4** | 2026-11-09 | **Widgets** (TON), ephemeral replies to callback queries, quotes from rich messages |
| **10.5** | 2026-11-22 | `setMySettings`, `BotFullInfo` from `getMe`, bot invite links, expandable quotation blocks |

## 2. Features worth adopting now

| Feature | What it gives you | Status in PTB 22.8 |
| :--- | :--- | :--- |
| Rich messages (`sendRichMessage`) | structured, streamable formatted messages | not wrapped → `do_api_request` |
| Ephemeral messages | group replies visible only to one user | not wrapped |
| Streaming drafts | partial AI answers | wrapped (`send_message_draft`) |
| Private-chat topics | forum-like organisation in DMs | partially wrapped |
| Checklists | native to-do lists | wrapped |
| Communities | several chats linked around a topic | partially wrapped |
| Widgets | interactive HTML/TON surfaces | not wrapped |
| `setMySettings` | bot changes its own settings | not wrapped |

Check what you have:

```python
import telegram
print(telegram.__version__, telegram.__bot_api_version__)   # e.g. 22.8 10.0
```

## 3. Calling an unwrapped method

```python
result = await context.bot.do_api_request(
    "setMySettings",
    {"inline_mode_settings": {...}},
)
```

`do_api_request` returns the raw JSON (or a `TelegramObject` if you pass `return_type`). It raises the same `TelegramError` subclasses as normal methods.

## 4. Behaviour changes to watch

| Change | Impact |
| :--- | :--- |
| Mini Apps: API calls from non-original origins blocked by default since 2026-07-20 | check your embeds and iframes |
| `getMe` returns `BotFullInfo` (10.5) | fields moved off `User`; update typed code |
| Poll `correct_option_id` → `correct_option_ids` (9.6) | quizzes can have several answers |
| Minimum poll options 2 → 1 (10.0) | validation code that assumed 2 must change |
| `sendMessageDraft` stop controls (10.3) | handle `stopped_message_generation` |
| `reply_parameters` gains `ephemeral_message_id` (10.2) | replies to ephemeral messages |

## 5. Migration strategy

1. Read the changelog for every version you skipped.
2. Bump the library first, then adopt features one at a time.
3. Keep a `do_api_request` escape hatch for anything not yet wrapped.
4. Test in the **dedicated test environment**: create a bot there with a separate @BotFather account and call
   `https://api.telegram.org/bot<token>/test/METHOD_NAME`. Test-server users are separate accounts, so use a
   Telegram client that can switch to the test server. Also test on iOS, Android and Desktop — rendering differs.

## Sources

- https://core.telegram.org/bots/api-changelog
- https://core.telegram.org/bots/webapps (origin protection, 2026-07-20)
- https://github.com/python-telegram-bot/python-telegram-bot/releases
