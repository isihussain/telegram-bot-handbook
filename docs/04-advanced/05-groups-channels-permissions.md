# Groups, Channels and Admin Rights

> **TL;DR:** Chat management is permissions work. Check your own rights before acting, promote/restrict with explicit permission objects, and treat join requests as untrusted input.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. What a bot can do where

| Chat type | Default bot powers | Requires admin |
| :--- | :--- | :--- |
| Private | send messages, ask for contact/location | — |
| Group | send messages, reply | delete, restrict, pin, invite links |
| Supergroup | same as group | topic management, `chat_member` updates |
| Channel | nothing | post, edit, delete, invite |

```python
me = await context.bot.get_chat_member(chat_id, context.bot.id)
print(me.status)                      # creator | administrator | member | ...
can_delete = getattr(me, "can_delete_messages", False)
```

## 2. Restrict, promote, ban

```python
from telegram import ChatPermissions

# mute until released
await context.bot.restrict_chat_member(
    chat_id=chat_id,
    user_id=user_id,
    permissions=ChatPermissions(can_send_messages=False),
)

# promote with the minimum set
await context.bot.promote_chat_member(
    chat_id=chat_id,
    user_id=user_id,
    can_delete_messages=True,
    can_restrict_members=True,
)

# ban (and unban with unban_chat_member)
await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
```

`restrict_chat_member` also accepts `until_date` for temporary mutes.

## 3. Join requests and guard bots

For chats with join requests enabled, you get `chat_join_request` updates:

```python
async def on_join_request(update, context):
    req = update.chat_join_request
    if req is None:
        return
    # Do not auto-approve on user-controlled fields alone.
    if await is_banned(req.user.id):
        await req.decline()
    else:
        await req.approve()
```

Bot API 10.1 added `query_id` on `ChatJoinRequest` and `answerChatJoinRequestQuery` / `sendChatJoinRequestWebApp`, so a guard bot can show a Mini App before deciding.

## 4. `chat_member` vs `my_chat_member`

| Update | Meaning |
| :--- | :--- |
| `my_chat_member` | the **bot's** status changed (added, promoted, removed) |
| `chat_member` | some **other** member's status changed; admins only, and must be in `allowed_updates` |

## 5. Channels

- A bot must be an **administrator** to post.
- `channel_post` and `edited_channel_post` are separate update fields from `message`.
- Comments live in a linked discussion group; the bot needs access there too.

```python
await context.bot.send_message(channel_id, "Release notes v1.2")
```

## 6. Anti-abuse basics

| Threat | Control |
| :--- | :--- |
| Flooding | per-user rate limit + `restrict_chat_member` |
| Spam links | allow/deny lists, delete + warn |
| Ban evasion | key on `user_id`, not username |
| Malicious files | validate type/size before forwarding |

See [../05-security/04-flood-and-abuse-control.md](../05-security/04-flood-and-abuse-control.md).

## 7. Pitfalls

- **Assuming admin rights** — always read your own status first; wrap calls in `try/except Forbidden`.
- **Username as identity** — usernames change; use numeric ids.
- **Restricting in channels** — some permissions cannot be set in channels.
- **Missing `allowed_updates`** — `chat_member` and reaction updates silently never arrive.

## Sources

- https://core.telegram.org/bots/api#chatmember
- https://core.telegram.org/bots/api#restrictchatmember
- https://core.telegram.org/bots/api#promotechatmember
- https://core.telegram.org/bots/api#chatjoinrequest
- https://core.telegram.org/bots/api-changelog (10.1 join request queries)
