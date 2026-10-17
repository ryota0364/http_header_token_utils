# http_header_token_utils

Parses HTTP header values containing RFC 7230 token and quoted-string elements, correctly handling escaping and obs-fold folding.

## Usage

```python
from http_header_token_utils import parse_token_or_quoted_string_list

elements = parse_token_or_quoted_string_list('gzip, "deflate", "a\\"b"')
# ['gzip', '"deflate"', '"a\\"b"']
```

## Why this exists

Parsing HTTP header values by splitting on commas silently breaks the moment a quoted-string contains an embedded comma, and naively stripping quotes discards backslash escaping. This library tokenises according to the RFC 7230 grammar, returning each element with its original syntax intact: quoted-strings keep their surrounding quotes and every `quoted-pair` is preserved verbatim. The single export is `parse_token_or_quoted_string_list`, which takes a raw header string and returns a list of element strings.

The deliberate trade-off is that this library does not interpret semantics (no parameter parsing, no quality value extraction). It is a pure tokeniser. If you need `Accept: text/html;q=0.9` split into a structured `(media-type, params)` representation, call this first then post-process the elements yourself.

## Edge cases

Obs-fold (CRLF followed by space or tab, from multi-line headers) is collapsed to a single space before tokenising. This means a folded header and its single-line equivalent parse identically. Inside a quoted-string, a backslash followed by any character is preserved exactly as written — no unescaping is performed. An unterminated quoted-string or a dangling backslash raises `ValueError`; non-string input raises `TypeError`.
