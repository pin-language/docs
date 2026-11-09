# Strings

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`ord`](#ord) | The first byte of a string as a number (0 to 255); 0 for `""`. |
| [`chr`](#chr) | A one-byte string with the byte `$n` (taken modulo 256, like PHP). |
| [`rawurlencode`](#rawurlencode) | Percent-encode everything but `A-Z a-z 0-9 - _ . ~`, for a value inside a URL path or query. |
| [`strlen`](#strlen) | Length of a string in bytes. |
| [`substr`](#substr) | Part of a string, by byte offsets. |
| [`mb_strlen`](#mb_strlen) | Length in characters (Unicode code points). |
| [`mb_substr`](#mb_substr) | Part of a string, counted in characters (code points). |
| [`mb_strpos`](#mb_strpos) | Position of the first match in characters, or -1. |
| [`mb_chr`](#mb_chr) | The character with this Unicode code point. |
| [`mb_ord`](#mb_ord) | The Unicode code point of the first character. |
| [`grapheme_strlen`](#grapheme_strlen) | Length in what people see as characters (grapheme clusters). |
| [`grapheme_substr`](#grapheme_substr) | Part of a string, counted in what people see as characters. **Use this to shorten text for display.** |
| [`strpos`](#strpos) | Byte position of the first match, or -1. |
| [`str_contains`](#str_contains) | Whether `$needle` occurs in `$haystack`. |
| [`str_starts_with`](#str_starts_with) | Whether `$s` begins with `$prefix`. |
| [`str_ends_with`](#str_ends_with) | Whether `$s` ends with `$suffix`. |
| [`str_repeat`](#str_repeat) | `$s` repeated `$times` times. |
| [`strtolower`](#strtolower) | Lower-case copy; only A–Z change. |
| [`strtoupper`](#strtoupper) | Upper-case copy; only a–z change. |
| [`trim`](#trim) | Copy without leading and trailing whitespace. |
| [`explode`](#explode) | Split a string into a list of strings. |
| [`implode`](#implode) | Join a list into one string. |
| [`PHP_EOL`](#php_eol) | The string `"\n"`. |

## ord

```php
ord(string $s): int
```

The first byte of a string as a number (0 to 255); 0 for `""`.

```php
echo ord("A"), " ", ord("a"), " ", ord(""), " ", ord("ไ"), "\n";
```

Output:

```
65 97 0 224
```

- A byte, not a character: Thai and other non-ASCII characters are several bytes.

## chr

```php
chr(int $n): string
```

A one-byte string with the byte `$n` (taken modulo 256, like PHP).

```php
echo chr(72), chr(105), chr(33 + 256), "\n";
```

Output:

```
Hi!
```

- A byte above 127 panics: alone it is not UTF-8, and every Pin string is valid UTF-8. `mb_chr($n)` gives the character with that code point.
- **PHP:** `chr(200)` gives one byte in PHP; in Pin it panics (use `mb_chr(200)` for "È").

## rawurlencode

```php
rawurlencode(string $s): string
```

Percent-encode everything but `A-Z a-z 0-9 - _ . ~`, for a value inside a URL path or query.

```php
echo "/search?q=" . rawurlencode("tea & cake/ไทย"), "\n";
```

Output:

```
/search?q=tea%20%26%20cake%2F%E0%B9%84%E0%B8%97%E0%B8%A2
```

- Spaces become `%20` (PHP's `urlencode` writes `+`; Pin has only this one).
- **PHP:** Same as PHP's `rawurlencode`.

## strlen

```php
strlen(string $s): int
```

Length of a string in bytes.

```php
echo strlen("hello"), " ", strlen("ไทย"), " ", strlen(""), "\n";
```

Output:

```
5 9 0
```

- Counts bytes, not characters: each Thai character is 3 bytes in UTF-8.

## substr

```php
substr(string $s, int $start, int $length = rest): string
```

Part of a string, by byte offsets.

```php
echo substr("hello world", 6), "|", substr("hello", -3), "|", substr("hello", 1, 3), "|", substr("hello", 1, -1), "|", substr("hi", 10), "|\n";
```

Output:

```
world|llo|ell|ell||
```

- A negative `$start` counts from the end; a negative `$length` stops that many bytes before the end.
- Out-of-range offsets give a shorter or empty string.
- Offsets are bytes. One that falls inside a character (each Thai character is 3 bytes) **panics** instead of giving broken text; positions from `strpos()` never do. To count characters use `mb_substr()`, to shorten text for display `grapheme_substr()`.
- **PHP:** The same, except that cutting a character in half panics instead of giving invalid UTF-8.

## mb_strlen

```php
mb_strlen(string $s): int
```

Length in characters (Unicode code points).

```php
echo mb_strlen("hello"), " ", mb_strlen("ไทย"), " ", mb_strlen("ที่"), "\n";
```

Output:

```
5 3 3
```

- A Thai tone mark or vowel above or below a letter is a code point of its own: `"ที่"` is 3. To count what a reader sees, use `grapheme_strlen()`.
- **PHP:** `mb_strlen($s)` with UTF-8; there is no encoding argument.

## mb_substr

```php
mb_substr(string $s, int $start, int $length = rest): string
```

Part of a string, counted in characters (code points).

```php
echo mb_substr("สวัสดีครับ", 0, 4), "|", mb_substr("สวัสดีครับ", -4), "|", mb_substr("abc", 5), "|\n";
```

Output:

```
สวัส|ครับ||
```

- The same rules as `substr()` for negative and out-of-range values, in code points.
- It can separate a tone mark from its letter (`mb_substr("ที่", 0, 2)` is `"ที"`); for text people read, use `grapheme_substr()`.
- **PHP:** `mb_substr()` with UTF-8.

## mb_strpos

```php
mb_strpos(string $haystack, string $needle): int
```

Position of the first match in characters, or -1.

```php
echo mb_strpos("ภาษาไทย", "ไทย"), " ", strpos("ภาษาไทย", "ไทย"), " ", mb_strpos("abc", "z"), "\n";
```

Output:

```
4 12 -1
```

- Use it with `mb_substr()`; `strpos()` gives bytes, for `substr()`.
- **PHP:** PHP returns `false` when not found; Pin returns `-1`.

## mb_chr

```php
mb_chr(int $codepoint): string
```

The character with this Unicode code point.

```php
echo mb_chr(3652), mb_chr(3607), mb_chr(3618), " ", mb_chr(128077), "\n";
```

Output:

```
ไทย 👍
```

- A value that is not a character (negative, above 0x10FFFF, or a surrogate 0xD800–0xDFFF) panics.
- **PHP:** PHP returns `false` for those.

## mb_ord

```php
mb_ord(string $s): int
```

The Unicode code point of the first character.

```php
echo mb_ord("ไ"), " ", mb_ord("A"), " ", mb_ord("👍"), "\n";
```

Output:

```
3652 65 128077
```

- `mb_ord("")` panics (PHP throws a ValueError).

## grapheme_strlen

```php
grapheme_strlen(string $s): int
```

Length in what people see as characters (grapheme clusters).

```php
echo grapheme_strlen("ที่นี่"), " ", mb_strlen("ที่นี่"), " ", grapheme_strlen("👨‍👩‍👧🇹🇭"), "\n";
```

Output:

```
2 6 2
```

- Unicode's extended grapheme clusters (UAX #29, Unicode 17): a Thai letter with its vowel and tone marks, an emoji with its skin tone or family members, a flag, are one each.
- ASCII is as fast as `mb_strlen()`; other text looks each code point up in a table (O(n)).
- **PHP:** `grapheme_strlen()` (PHP's intl extension).

## grapheme_substr

```php
grapheme_substr(string $s, int $start, int $length = rest): string
```

Part of a string, counted in what people see as characters. **Use this to shorten text for display.**

```php
$title = "ที่นี่มีน้ำใจ";
echo grapheme_substr($title, 0, 4), "…|", mb_substr($title, 0, 4), "…|", grapheme_substr($title, -2), "\n";
```

Output:

```
ที่นี่มีน้ำ…|ที่น…|ใจ
```

- The same rules as `substr()` for negative and out-of-range values, in grapheme clusters.
- Never separates a tone mark or vowel from its letter, or an emoji from its modifier.
- **PHP:** `grapheme_substr()`; PHP returns `false` when `$start` is past the end, Pin returns `""`.

## strpos

```php
strpos(string $haystack, string $needle): int
```

Byte position of the first match, or -1.

```php
echo strpos("hello", "ll"), " ", strpos("hello", "z"), " ", strpos("abc", ""), "\n";
```

Output:

```
2 -1 0
```

- An empty needle matches at 0.
- **PHP:** PHP returns `false` when not found; Pin returns `-1`, so write `strpos($s, $x) < 0`. There is no offset argument yet.

## str_contains

```php
str_contains(string $haystack, string $needle): bool
```

Whether `$needle` occurs in `$haystack`.

```php
echo str_contains("pineapple", "apple") ? "yes" : "no", "\n";
```

Output:

```
yes
```

## str_starts_with

```php
str_starts_with(string $s, string $prefix): bool
```

Whether `$s` begins with `$prefix`.

```php
echo str_starts_with("/user/42", "/user/") ? "yes" : "no", "\n";
```

Output:

```
yes
```

## str_ends_with

```php
str_ends_with(string $s, string $suffix): bool
```

Whether `$s` ends with `$suffix`.

```php
echo str_ends_with("photo.png", ".png") ? "yes" : "no", "\n";
```

Output:

```
yes
```

## str_repeat

```php
str_repeat(string $s, int $times): string
```

`$s` repeated `$times` times.

```php
echo str_repeat("ab", 3), "|", str_repeat("x", 0), "|\n";
```

Output:

```
ababab||
```

- A negative count panics; a result too large to allocate panics.

## strtolower

```php
strtolower(string $s): string
```

Lower-case copy; only A–Z change.

```php
echo strtolower("Hello ÄB ไทย"), "\n";
```

Output:

```
hello Äb ไทย
```

- Non-ASCII letters are left as they are (PHP 8.2+ behaves the same).

## strtoupper

```php
strtoupper(string $s): string
```

Upper-case copy; only a–z change.

```php
echo strtoupper("mixed Case"), "\n";
```

Output:

```
MIXED CASE
```

## trim

```php
trim(string $s): string
```

Copy without leading and trailing whitespace.

```php
echo "[", trim("  padded \n"), "]\n";
```

Output:

```
[padded]
```

- Removes spaces, tabs, `\n`, `\r` and `\v`. There is no second argument yet.

## explode

```php
explode(string $separator, string $s): list<string>
```

Split a string into a list of strings.

```php
echo json_encode(explode(",", "a,b,,c")), " ", count(explode(",", "")), "\n";
```

Output:

```
["a","b","","c"] 1
```

- Empty pieces are kept. Splitting an empty string gives one empty piece.
- An empty separator panics (PHP throws a ValueError).
- **PHP:** Same argument order as PHP. There is no `$limit` argument yet.

## implode

```php
implode(string $glue, list<string|int|float> $xs): string
```

Join a list into one string.

```php
echo implode(", ", ["tea", "cake"]), " | ", implode("-", [1, 2, 3]), "\n";
```

Output:

```
tea, cake | 1-2-3
```

- Works on `list<string>`, `list<int>` and `list<float>`, not `list<bool>`.
- **PHP:** Only the `implode($glue, $list)` order is accepted.

## PHP_EOL

```php
PHP_EOL: string
```

The string `"\n"`.

```php
echo "line", PHP_EOL;
```

Output:

```
line
```
