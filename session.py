import base64, zlib, json

c = ""
raw = base64.urlsafe_b64decode(c + "=" * (-len(c) % 4))
print(zlib.decompress(raw))