# Strings

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`strlen`](#strlen) | Length of a string in bytes. |
| [`substr`](#substr) | Part of a string, by byte offsets. |
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
- Out-of-range offsets give a shorter or empty string, never a panic.
- Offsets are bytes: cutting inside a Thai character gives broken text.

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
