from __future__ import annotations

__all__ = ["parse_token_or_quoted_string_list"]


def _unfold(header_value: str) -> str:
    """Collapse obs-fold (CRLF followed by SP / HTAB) into a single SP.

    RFC 7230 §3.2.4 deprecated obs-fold, but §3.2.4 says a recipient MAY
    replace it with a single SP before interpreting the field value. We do
    exactly that so a folded header and a single-line header parse
    identically. Using a character replacement here is safe because the
    only valid obs-fold sequence is CR LF (SP|HTAB); a bare CR or LF inside
    a quoted-string is not a legal header character, so the replacement is
    unambiguous.
    """
    result_chars: list[str] = []
    i = 0
    length = len(header_value)
    while i < length:
        ch = header_value[i]
        if ch == "\r" and i + 2 < length and header_value[i + 1] == "\n" and header_value[i + 2] in (" ", "\t"):
            result_chars.append(" ")
            i += 3
        elif ch == "\n" and i + 1 < length and header_value[i + 1] in (" ", "\t"):
            # Tolerant variant of obs-fold: bare LF followed by whitespace.
            result_chars.append(" ")
            i += 2
        else:
            result_chars.append(ch)
            i += 1
    return "".join(result_chars)


def _is_token_char(ch: str) -> bool:
    return ch.isascii() and ch.isprintable() and ch not in (" ", "\t") and ch not in "()<>@,;:\\\"/[]?={}"


def parse_token_or_quoted_string_list(header_value: str) -> list[str]:
    """Parse an HTTP header value into RFC 7230 tokens and quoted-strings.

    Grammar (RFC 7230 §3.2.6, §3.2.3):

        token          = 1*<tchar>
        quoted-string  = DQUOTE *( qdtext / quoted-pair ) DQUOTE
        qdtext         = HTAB / SP / %x21 / %x23-5B / %x5D-7E
        quoted-pair   = "\\" ( HTAB / SP / VCHAR / obs-text )

    The header value is first unfolded per §3.2.4, then tokenised. Each
    element is returned exactly as it appears syntactically: a quoted-string
    retains its surrounding double quotes and all backslash escapes are
    preserved verbatim. A bare token is returned as-is. Whitespace and
    commas between elements are treated as delimiters and discarded.

    Raises ValueError on malformed input: an unterminated quoted-string,
    a stray backslash with no following character, an unescaped quote
    inside a token, or an illegal character.

    Args:
        header_value: The raw HTTP header value (may include obs-fold
            continuations from multi-line headers).

    Returns:
        A list of element strings, in the order they appeared. An empty
        header value yields an empty list.
    """
    if not isinstance(header_value, str):
        raise TypeError(f"expected str, got {type(header_value).__name__}")

    text = _unfold(header_value)
    elements: list[str] = []
    i = 0
    length = len(text)

    while i < length:
        ch = text[i]

        if ch in (" ", "\t", ","):
            i += 1
            continue

        if ch == '"':
            element_chars: list[str] = ['"']
            j = i + 1
            while j < length:
                cj = text[j]
                if cj == "\\":
                    if j + 1 >= length:
                        raise ValueError("unterminated quoted-string: dangling backslash")
                    element_chars.append(cj)
                    element_chars.append(text[j + 1])
                    j += 2
                    continue
                if cj == '"':
                    element_chars.append('"')
                    j += 1
                    break
                element_chars.append(cj)
                j += 1
            else:
                raise ValueError("unterminated quoted-string: missing closing DQUOTE")
            elements.append("".join(element_chars))
            i = j
            continue

        if _is_token_char(ch):
            start = i
            i += 1
            while i < length and _is_token_char(text[i]):
                i += 1
            elements.append(text[start:i])
            continue

        raise ValueError(f"illegal character {ch!r} at position {i}")

    return elements
