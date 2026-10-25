# Pin — Strings and Thai text

**Status (Pin 0.4, 2026-10-25):** **mostly not built yet.** Today strings are bytes like PHP: `strlen`,
`substr` and `strpos` count bytes, and nothing validates UTF-8 or protects against cutting a character in half.
Built since this design: `list<string>`, `explode`, `implode`, `sort` (0.2), and JSON output keeps UTF-8 as is.
The rules below (UTF-8 invariant, character-aware functions, normalisation) are agreed with the owner
(2026-10-24) but not implemented.

Decision rule: memory safety > speed > clarity > looking like PHP.

## Facts (checked with Python's unicodedata)

- `"ไทย"` is 3 characters and 9 bytes.
- `"ที่"` is 3 code points (ท + ี + ่) and 9 bytes, but people see one character cell.
- `"ำ"` (U+0E33) has a compatibility decomposition to U+0E4D U+0E32, so NFKC makes the two spellings equal;
  NFC does not.

## Rules

### ST1 — `string` is always valid UTF-8 (an invariant)
- Checked only at the edges: request path and body, files, the database, `bytes_to_string()`.
- Operations on valid strings give valid strings, so nothing is checked twice: `.`, `.=`, interpolation,
  `str_repeat`, `strtolower`, `trim`, `json_encode`, `substr` (with ST3).
- Validated with SIMD (like simdutf), at gigabytes per second.
- Overlong encodings, surrogates (U+D800–DFFF) and values above U+10FFFF are rejected.
- A request whose path or body is not valid UTF-8 gets a 400 from the server without reaching the handler
  (except handlers that take `bytes`, once ST2 exists).

### ST2 — `bytes` for binary data (later)
- Uploaded files, images, hashes, encrypted data.
- Cannot be used as a `string`: `bytes_to_string(bytes $b): string throws`; `string_to_bytes()` never fails.
- Not needed in the first step.

### ST3 — `strlen` / `substr` / `strpos` count bytes, O(1)
- Same names and meaning as PHP (`strpos` returns -1 when not found, as now).
- A `substr` whose start or end falls inside a character **panics**:
```
text.pn:4: panic: substr() would cut a character in half at byte 4 of "ไทย".
  Use mb_substr() to count characters, or grapheme_substr() to count what people see
```
- Positions from `strpos` / `str_*` never fall inside a character (the needle is valid UTF-8), so
  `substr($s, strpos($s, $x))` never panics.

### ST4 — counting characters: PHP's existing names
| function | counts | `"ที่"` | speed |
|---|---|---|---|
| `strlen` | bytes | 9 | O(1) |
| `mb_strlen` / `mb_substr` / `mb_strpos` | code points | 3 | O(n) |
| `grapheme_strlen` / `grapheme_substr` | what people see (UAX #29) | 1 | O(n) |

- **To shorten Thai text for display, use `grapheme_substr`** (otherwise tone marks and vowels come loose).
- Strings remember whether they are pure ASCII (computed during ST1 validation or when built), so `mb_*` and
  `grapheme_*` are as fast as `strlen` on ASCII text.
- Layout stays `{len, cap, bytes}` plus a 1-bit flag (in the high bit of `cap` or a new field — decide when
  building it).

### ST5 — letter case
- `strtolower` / `strtoupper` change A–Z only (like PHP 8.2+), independent of locale (as now).
- `mb_strtolower` / `mb_strtoupper` for Unicode.
- Thai has no letter case, so it is unaffected.

### ST6 — normalisation: not automatic, available
- `normalizer_normalize(string $s, int $form): string` with `NFC` and `NFKC`.
- The docs must say plainly: **usernames, emails and lookup keys → NFKC before storing and before comparing**
  (the "ำ" case allows look-alike names).

### ST7 — not planned now (needs ICU; a library later)
- Thai dictionary order (`<` compares code points; leading vowels เ แ โ ใ ไ put words in the wrong order).
- Thai word breaking (no spaces between words).
- Thai digits ๑๒๓ in `intval()` — not supported (ASCII only, like PHP).

## Runtime work when this is built

1. A UTF-8 validator (a correct scalar one first, then SIMD with the same tests).
2. A boundary check in `pn_substr` (the byte at the position must not be `10xxxxxx`).
3. `mb_*` and `grapheme_*` (the Unicode Grapheme_Cluster_Break table — only the needed ranges, or the whole
   table, a few KB).
4. Tests: Thai, emoji, combining marks, overlong (`C0 AF`), surrogates (`ED A0 80`), cutting inside a
   character → panic.
