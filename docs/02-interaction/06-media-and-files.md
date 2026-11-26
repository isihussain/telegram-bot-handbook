# Media: Files, Photos, `file_id`

> **TL;DR:** Upload once, reuse `file_id` forever. Downloading is capped at 20 MB and uploading at 50 MB; a local Bot API server lifts both. Always validate size and type before sending.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Sending media

| Method | Content | Limits |
| :--- | :--- | :--- |
| `sendPhoto` | compressed image | 10 MB upload, dimensions are re-encoded |
| `sendDocument` | any file, no re-encoding | 50 MB |
| `sendVideo`, `sendAudio`, `sendVoice`, `sendAnimation` | media types | 50 MB |
| `sendMediaGroup` | album | 2–10 items |
| `sendSticker` | `.webp`/`.tgs`/`.webm` | 50 MB |

```python
# upload from disk
await update.message.reply_document(document=open("report.pdf", "rb"))

# or send by id (no upload, instant)
await context.bot.send_document(chat_id=chat_id, document=file_id)
```

## 2. The `file_id` rule

```mermaid
flowchart LR
    U["Upload once"] --> F["file_id"]
    F --> R1["re-send: same file_id"]
    F --> R2["store in DB"]
    R2 --> R1
```

- `file_id` is **persistent** and safe to store.
- `file_unique_id` is stable across bots; `file_id` is specific to your bot.
- You cannot change the type when re-sending (`file_id` of a video cannot be sent as a photo).
- Re-sending by `file_id` is free of upload cost and far faster.

```python
msg = await update.message.reply_document(document=open("a.pdf", "rb"))
file_id = msg.document.file_id          # store this
```

## 3. Downloading

```python
file = await context.bot.get_file(update.message.document.file_id)
await file.download_to_drive("incoming.pdf")     # 20 MB limit on the public API
```

| Limit | Public API | Local Bot API server |
| :--- | :--- | :--- |
| Download | **20 MB** | no limit |
| Upload | **50 MB** | **2000 MB** |

For bigger files, run your own Bot API server: [../04-advanced/06-local-bot-api-server.md](../04-advanced/06-local-bot-api-server.md).

## 4. Validate before you forward

Never forward user uploads blindly. Check size, MIME type and extension, and store them outside the web root.

```python
MAX_BYTES = 20 * 1024 * 1024

async def on_document(update, context):
    doc = update.message.document
    if doc.file_size and doc.file_size > MAX_BYTES:
        await update.message.reply_text("File is too large.")
        return
    if doc.mime_type not in {"application/pdf", "text/plain"}:
        await update.message.reply_text("Only PDF and TXT are accepted.")
        return
    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(f"uploads/{doc.file_unique_id}.bin")
```

## 5. Albums and groups

```python
from telegram import InputMediaPhoto

await context.bot.send_media_group(
    chat_id=chat_id,
    media=[InputMediaPhoto(open("1.jpg", "rb")), InputMediaPhoto(open("2.jpg", "rb"))],
)
```

Captions apply to the first item only, and albums arrive as several separate `message` updates with the same `media_group_id`.

## 6. Pitfalls

- **Sending `open()` without closing** — use `with` or pass bytes; the library uploads immediately but leaking descriptors adds up.
- **Assuming `file_id` works for another bot** — it does not.
- **Expecting original quality** — `sendPhoto` re-encodes; use `sendDocument` to preserve bytes.
- **`getFile` on a >20 MB file** — fails on the public API.

## Sources

- https://core.telegram.org/bots/api#sending-files
- https://core.telegram.org/bots/api#getfile
- https://core.telegram.org/bots/api#senddocument
- https://core.telegram.org/bots/api#sendmediagroup
