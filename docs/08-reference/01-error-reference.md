# Error Reference

> **TL;DR:** The `description` string is the real error message; `error_code` is the class. Search the description below before opening an issue.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

| Description (contains) | Code | Meaning | Fix |
| :--- | :--- | :--- | :--- |
| `Unauthorized` | 401 | bad or revoked token | new token from @BotFather |
| `chat not found` | 400 | wrong `chat_id`, bot never saw the chat, or it was deleted | verify id, user must `/start` first |
| `bot was blocked by the user` | 403 | user blocked the bot | stop sending, prune |
| `user is deactivated` | 403 | account deleted | prune |
| `not enough rights` | 400 | bot lacks the admin right | grant it |
| `message is too long` | 400 | > 4096 characters | split |
| `can't parse entities` | 400 | bad HTML/MarkdownV2 | escape input |
| `BUTTON_DATA_INVALID` | 400 | `callback_data` > 64 bytes or bad UTF-8 | shorten |
| `message is not modified` | 400 | edit produced no change | ignore |
| `message to edit not found` | 400 | original deleted | send a new message |
| `query is too old` | 400 | callback answered too late | answer immediately |
| `wrong file identifier` | 400 | `file_id` from another bot | re-upload |
| `file is too big` | 400 | over 20 MB download / 50 MB upload | local Bot API server |
| `Too Many Requests` | 429 | rate limited | sleep `retry_after` |
| `terminated by other getUpdates` | 409 | two pollers | run one |
| `can't use getUpdates while webhook is active` | 409 | both modes | `deleteWebhook` |
| `chat was upgraded to a supergroup` | 400 | group migrated | use `ChatMigrated.new_chat_id` |
| `have no rights to send a message` | 400 | restricted chat | check permissions |
| `not a member of the chat` | 403 | removed | re-add or stop |
| `invoice payload is invalid` | 400 | payload length/charset | 1–128 bytes |

## Reading the error in code

```python
from telegram.error import BadRequest

try:
    await bot.send_message(chat_id, text)
except BadRequest as exc:
    if "chat not found" in str(exc):
        ...
```

Match on substrings only as a last resort: descriptions can change. Prefer checking the exception class, then the code, then the text.

## Related pages

- [../06-production/03-errors-429-and-retries.md](../06-production/03-errors-429-and-retries.md)
- [../01-foundations/05-limits-cheatsheet.md](../01-foundations/05-limits-cheatsheet.md)
- [../06-production/06-troubleshooting.md](../06-production/06-troubleshooting.md)

## Sources

- https://core.telegram.org/bots/api#making-requests
- https://core.telegram.org/bots/api#responseparameters
- https://docs.python-telegram-bot.org/en/stable/telegram.error.html
