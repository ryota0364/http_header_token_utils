"""http_header_token_utils: parse HTTP header token and quoted-string elements.

This package exposes :func:`parse_token_or_quoted_string_list`, which
splits an HTTP header value into RFC 7230 tokens and quoted-strings while
honouring backslash escaping and obs-fold line continuation.
"""

from http_header_token_utils.core import parse_token_or_quoted_string_list

__all__ = ["parse_token_or_quoted_string_list"]
