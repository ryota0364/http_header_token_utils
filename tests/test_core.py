import unittest

from http_header_token_utils import parse_token_or_quoted_string_list


class TestParseTokenOrQuotedStringList(unittest.TestCase):
    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse_token_or_quoted_string_list(""), [])

    def test_single_token(self):
        self.assertEqual(parse_token_or_quoted_string_list("gzip"), ["gzip"])

    def test_multiple_tokens_space_delimited(self):
        self.assertEqual(
            parse_token_or_quoted_string_list("gzip deflate"),
            ["gzip", "deflate"],
        )

    def test_multiple_tokens_comma_delimited(self):
        self.assertEqual(
            parse_token_or_quoted_string_list("gzip, deflate"),
            ["gzip", "deflate"],
        )

    def test_mixed_comma_and_space_delimiters(self):
        self.assertEqual(
            parse_token_or_quoted_string_list("gzip, deflate, br"),
            ["gzip", "deflate", "br"],
        )

    def test_quoted_string_preserves_quotes(self):
        self.assertEqual(
            parse_token_or_quoted_string_list('"gzip, deflate"'),
            ['"gzip, deflate"'],
        )

    def test_quoted_string_with_escaped_quote(self):
        self.assertEqual(
            parse_token_or_quoted_string_list(r'"a\"b"'),
            [r'"a\"b"'],
        )

    def test_quoted_string_with_escaped_backslash(self):
        self.assertEqual(
            parse_token_or_quoted_string_list(r'"a\\b"'),
            [r'"a\\b"'],
        )

    def test_quoted_string_with_internal_comma(self):
        self.assertEqual(
            parse_token_or_quoted_string_list('"a, b", gzip'),
            ['"a, b"', "gzip"],
        )

    def test_obs_fold_crlf_replaced_with_space(self):
        header = "gzip\r\n deflate"
        self.assertEqual(parse_token_or_quoted_string_list(header), ["gzip", "deflate"])

    def test_obs_fold_in_quoted_string(self):
        header = '"gzip\r\n deflate"'
        self.assertEqual(
            parse_token_or_quoted_string_list(header),
            ['"gzip deflate"'],
        )

    def test_multiple_quoted_pairs_preserved(self):
        self.assertEqual(
            parse_token_or_quoted_string_list(r'"\a\b\c"'),
            [r'"\a\b\c"'],
        )

    def test_extra_whitespace_between_elements(self):
        self.assertEqual(
            parse_token_or_quoted_string_list("gzip   ,   deflate"),
            ["gzip", "deflate"],
        )

    def test_unterminated_quoted_string_raises(self):
        with self.assertRaises(ValueError):
            parse_token_or_quoted_string_list('"unterminated')

    def test_dangling_backslash_raises(self):
        with self.assertRaises(ValueError):
            parse_token_or_quoted_string_list(r'"abc\\')

    def test_illegal_control_character_raises(self):
        with self.assertRaises(ValueError):
            parse_token_or_quoted_string_list("gzip\x01deflate")

    def test_non_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            parse_token_or_quoted_string_list(123)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
