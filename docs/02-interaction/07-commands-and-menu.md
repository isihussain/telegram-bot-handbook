# Commands and the Menu Button

> **TL;DR:** Register commands with `setMyCommands` (per scope and language) so users get autocomplete, and use `setChatMenuButton` to point the menu at a Mini App or a command list. Names are 1–32 characters, descriptions 1–256.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Register commands at startup

```python
from telegram import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

await app.bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("help", "How to use it"),
    BotCommand("buy", "Buy premium"),
])

# different commands for admins
await app.bot.set_my_commands(
    [BotCommand("stats", "Usage statistics")],
    scope=BotCommandScopeChat(chat_id=ADMIN_ID),
)
```

Do it in `post_init`, once per process start, not on every update.

## 2. Scopes

| Scope | Applies to |
| :--- | :--- |
| `BotCommandScopeDefault` | everyone, unless a narrower scope applies |
| `BotCommandScopeAllPrivateChats` | all private chats |
| `BotCommandScopeAllGroupChats` | all groups |
| `BotCommandScopeAllChatAdministrators` | admins in any chat |
| `BotCommandScopeChat(chat_id)` | one chat |
| `BotCommandScopeChatAdministrators(chat_id)` | admins of one chat |
| `BotCommandScopeChatMember(chat_id, user_id)` | one member of one chat |

Narrower scopes win. Delete an override with `delete_my_commands(scope=...)`.

## 3. Localisation

```python
await app.bot.set_my_commands(
    [BotCommand("start", "Başla"), BotCommand("help", "Yardım")],
    language_code="tr",
)
```

The client picks the list matching the user's language, falling back to the default.

## 4. Menu button

```python
from telegram import MenuButtonWebApp, WebAppInfo, MenuButtonCommands

# point the menu at a Mini App
await app.bot.set_chat_menu_button(
    menu_button=MenuButtonWebApp(text="Open app", web_app=WebAppInfo(url="https://app.example.com"))
)

# or back to the command list
await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
```

`set_chat_menu_button` without `chat_id` changes the default for all users.

## 5. Parsing commands

```python
from telegram.ext import CommandHandler

app.add_handler(CommandHandler("start", start))
```

`CommandHandler` also matches `/start@mybot` in groups, which is required when several bots share a group.

| Input | `context.args` |
| :--- | :--- |
| `/buy` | `[]` |
| `/buy premium` | `["premium"]` |
| `/buy@mybot premium 30d` | `["premium", "30d"]` |

## 6. Unknown commands

Telegram does not send a "command not found" event. Add a catch-all and be explicit:

```python
from telegram.ext import MessageHandler, filters

async def unknown(update, context):
    await update.message.reply_text("Unknown command. Try /help.")

app.add_handler(MessageHandler(filters.COMMAND, unknown))
```

Register it **after** the real command handlers.

## 7. Pitfalls

- **Commands with spaces or uppercase** are rejected; use lowercase `a-z`, digits and `_`.
- **Registering on every update** wastes a call and can hit rate limits.
- **Assuming the menu is a command list** — it can be a Mini App, and users can override it per chat.

## Sources

- https://core.telegram.org/bots/api#setmycommands
- https://core.telegram.org/bots/api#botcommandscope
- https://core.telegram.org/bots/api#setchatmenubutton
- https://core.telegram.org/bots/features#commands
