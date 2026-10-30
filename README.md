# Flask Session Cookie Decoder

A tiny Python script that decodes the **payload** of a Flask session cookie (URL-safe Base64 + zlib compression) so you can read what's stored inside it. It's useful for debugging, learning how signed cookies work, and CTF-style challenges.

> **Note:** Decoding a Flask cookie does **not** require the secret key. The cookie is *signed* (tamper-proof), not *encrypted*. Anyone who has the cookie can read its contents, so never store secrets in a Flask session.

## Requirements

- Python 3.x
- No external dependencies (standard library only)

## Getting the Cookie

1. Open the site in your browser and log in.
2. Press **F12** to open Developer Tools.
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. Expand **Cookies** in the sidebar and select the site.
5. Find the `session` cookie and **copy its value**.

## Cookie Structure

A Flask session cookie is made of parts separated by `.` (dots):

```
.eJwty0sKgCAQANC7zFrCxqz0...VFHFs.auPybQ.C-QHeUrYJT6J4c5QVBZ1MEfA8U0
│└──────────┬───────────────────┘ └─┬──┘ └────────────┬────────────┘
│         payload               timestamp           signature
└─ leading dot = payload is zlib-compressed
```

| Part | Example | Meaning |
|------|---------|---------|
| **Leading `.`** | `.` | A flag meaning the payload was compressed with zlib before being Base64-encoded. If the cookie has no leading dot, the payload is plain Base64 with no compression. |
| **Payload** | `eJwty0sKgCAQ...VFHFs` | The session data (JSON), zlib-compressed, then URL-safe Base64 encoded. **This is the part you decode.** |
| **Timestamp** | `auPybQ` | A URL-safe Base64 encoded big-endian integer: the Unix time (in seconds) when the cookie was signed. Here it decodes to `1793323629`, which is `2026-10-30 01:27:09 UTC`. |
| **Signature** | `C-QHeUrYJT6J4c5QVBZ1MEfA8U0` | An HMAC-SHA1 signature (20 raw bytes, Base64 encoded) made with the app's `SECRET_KEY`. It lets the server detect tampering. It is not compressed data and can't be decoded into anything readable. |

## Usage

**Paste only the payload** into the variable `c`. That is the second chunk, between the first `.` and the second `.`, **without** the leading dot.

Given this full cookie:

```
.eJwty0sKgCAQANC7zFrCxqz0MiE5ieAPtVV091y0ffAeCNk5sqDhMqERMMi9HI3OSn2gkhx_6z5S6yYW0POmhECxoppw4WKXksHdqCYTaSRjo0_wfkVBHFs.auPybQ.C-QHeUrYJT6J4c5QVBZ1MEfA8U0
```

Set `c` to just the payload:

```python
import base64, zlib, json

c = "eJwty0sKgCAQANC7zFrCxqz0MiE5ieAPtVV091y0ffAeCNk5sqDhMqERMMi9HI3OSn2gkhx_6z5S6yYW0POmhECxoppw4WKXksHdqCYTaSRjo0_wfkVBHFs"
raw = base64.urlsafe_b64decode(c + "=" * (-len(c) % 4))
print(zlib.decompress(raw))
```

Run it:

```bash
python decode.py
```

### Output

```
b'{"logged":"false","otp_secret":"9502","otp_timestamp":1793323629.2403855,"username":"admin"}'
```

## Why You Shouldn't Paste the Whole Cookie

Pasting the entire cookie into `c` will fail, for a few reasons:

1. **The dots aren't valid Base64.** `.` is not part of the URL-safe Base64 alphabet (`A-Z a-z 0-9 - _`), so the decoder will choke or return garbage.
2. **Only the payload is zlib-compressed.** The timestamp and signature are separate Base64 chunks of raw bytes. If they got mixed into the payload, `zlib.decompress` would raise a `zlib.error` (invalid header or corrupted data).
3. **The leading dot is a flag, not data.** It tells you the payload is compressed, but it isn't part of the Base64 string itself, so it must be removed.
4. **Padding breaks.** The script adds `=` padding based on the string length. Extra chunks change the length and corrupt the decoding.

In short: split the cookie on `.` and decode only the payload chunk.

## Optional Tweaks

Print as readable text instead of bytes:

```python
print(zlib.decompress(raw).decode("utf-8"))
```

Parse and pretty-print the JSON (this is what the `json` import is for):

```python
print(json.dumps(json.loads(zlib.decompress(raw)), indent=2))
```

Decode the timestamp too:

```python
import datetime
ts = int.from_bytes(base64.urlsafe_b64decode("auPybQ=="), "big")
print(datetime.datetime.fromtimestamp(ts, datetime.timezone.utc))
```

## Troubleshooting

| Error | Likely cause |
|-------|--------------|
| `zlib.error: Error -3 while decompressing data: incorrect header check` | The cookie has no leading dot (not compressed), or you pasted the wrong chunk. |
| `binascii.Error: Incorrect padding` / invalid characters | You included dots or other parts of the cookie, or copied it with extra characters. |
| `UnicodeDecodeError` after `.decode()` | The decompressed data isn't UTF-8 text. |

## Disclaimer

For educational purposes and for debugging applications you own or are authorized to test.

## License

Released under the [MIT License](LICENSE).
