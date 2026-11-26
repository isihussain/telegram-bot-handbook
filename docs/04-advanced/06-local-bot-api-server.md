# Local Bot API Server

> **TL;DR:** Running `telegram-bot-api` yourself lifts the 20 MB download and 50 MB upload limits, allows any webhook port and a plain-HTTP webhook, and gives you local file paths. It needs `api_id`/`api_hash` and is a bigger operational commitment.
> **Applies to:** Bot API 10.5 · telegram-bot-api (tdlib) · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. What changes

| Capability | Public API | Local server (`--local`) |
| :--- | :--- | :--- |
| Download | 20 MB | no limit |
| Upload | 50 MB | **2000 MB** |
| Upload by local path / `file://` | no | yes |
| Webhook URL | HTTPS only | HTTP allowed |
| Webhook host | public IP | any local IP |
| Webhook port | 443/80/88/8443 | any |
| `max_webhook_connections` | 1–100 | up to 100000 |
| `getFile` result | download via HTTPS | absolute local path |

## 2. Build and run

```bash
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --target install

telegram-bot-api --api-id="$API_ID" --api-hash="$API_HASH" \
  --local --http-port=8081 \
  --dir=/var/lib/telegram-bot-api
```

Get `api_id`/`api_hash` from <https://my.telegram.org>. The server speaks plain HTTP on port 8081 by default; put a TLS proxy in front for remote access.

## 3. Point the bot at it

```python
app = (
    ApplicationBuilder()
    .token(token)
    .base_url("http://127.0.0.1:8081/bot")
    .base_file_url("http://127.0.0.1:8081/file/bot")
    .local_mode(True)
    .build()
)
```

`local_mode(True)` tells the library that `getFile` returns local paths and that it may use them directly.

## 4. Moving a bot between servers

1. `logOut` on the old server (guarantees no updates are lost on the old side).
2. `deleteWebhook` and `close` on the old instance.
3. Start on the new server.

```python
await bot.log_out()
await bot.delete_webhook()
await bot.close()
```

## 5. Operational reality

| Concern | Notes |
| :--- | :--- |
| State | local server keeps its own state in `--dir`; back it up |
| Updates | one local server per token |
| Resources | CPU/disk for file storage; plan capacity |
| Security | it is an unauthenticated HTTP API on localhost — never expose it |
| Compliance | you now store user files; apply retention and access rules |

## 6. When it is worth it

- You must accept files larger than 50 MB.
- You process media and want to avoid a second download.
- You need webhooks on a non-standard port behind an internal network.

Otherwise, the public API plus object storage is simpler.

## Sources

- https://github.com/tdlib/telegram-bot-api (README: local mode capabilities)
- https://core.telegram.org/bots/api#using-a-local-bot-api-server
- https://docs.python-telegram-bot.org/en/stable/telegram.ext.applicationbuilder.html (`base_url`, `local_mode`)
