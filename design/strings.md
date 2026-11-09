# Pin — Strings and Thai text

**Status (2026-11-09):** ST1, ST3, ST4, ST5 and ST6 are **built** on `next` (see "As built" at the end): strings
are always valid UTF-8, `substr()` panics rather than cut a character, `mb_strlen` / `mb_substr` / `mb_strpos` /
`mb_chr` / `mb_ord`, `grapheme_strlen` / `grapheme_substr`, `mb_strtolower` / `mb_strtoupper`,
`normalizer_normalize()`. Not built: ST2 (`bytes`), the SIMD validator and the ASCII flag of ST4; ST7 stays out.

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

## As built (2026-11-09)

- **ST1, where text comes in:** the request line (method and path) and the body are checked before the handler
  runs; a request that is not UTF-8 gets **400**. Everything else from outside has bad bytes replaced by U+FFFD,
  WHATWG-style (one per "maximal subpart"): request headers, values decoded from `%XX` (`query_param`,
  `form_param`: `%C8` alone is not UTF-8), `db_string` / `db_json` / `db_error` (a SQLite TEXT column can hold
  any bytes, so can PostgreSQL's SQL_ASCII), `http_get` / `http_post` / `stream_next` answers, `run()` output,
  `read_line()`, `env()`, and every error message (they quote other servers' answers cut at a byte limit).
  Reason for replacing instead of failing: these are not requests to refuse, and most have no error path.
  JSON `\u` escapes were already safe: a lone surrogate is U+FFFD in `json_string()` and an error (400) in
  `json_decode()`. Source files must be UTF-8 (the compiler checks), so literals are valid.
- **`chr()` above 127 panics** (it would make a lone byte). This is the one place Pin breaks PHP for ST1;
  `mb_chr()` gives the character. `tests/bytes.pn` had built all 256 bytes and now builds 128.
- **Validator:** scalar, eight ASCII bytes at a time, not SIMD yet. Measured cost on the HTTP path: see the
  numbers in HANDOFF (a request is checked once, path and body only).
- **ST3:** `substr()` checks that neither end falls on a continuation byte (`10xxxxxx`); the panic names the
  character and its bytes. `strpos()` results never fail it.
- **ST4:** `mb_*` count code points (O(n), no ASCII flag yet). `grapheme_*` follow UAX #29 extended grapheme
  clusters, all rules including GB9c (Indic conjuncts) and GB11 (emoji ZWJ sequences), from a table generated
  by `tools/gen_unicode.py` out of Python 3.15's `unicodedata` (Unicode 17.0, 2,168 ranges, 27 KB) — no
  download, no ICU. `tools/check_unicode.py` compares Pin with Python's `unicodedata.iter_graphemes()` on random
  strings of every property: 100,000 strings, 0 differences. `mb_chr()` of a non-character panics (PHP returns
  `false`); `mb_ord("")` panics (PHP throws).
- **ST5:** `mb_strtolower` / `mb_strtoupper` use Unicode's full mappings (`ß` → `SS`) and the final-sigma rule
  (Σ → ς at the end of a word, as PHP 8.3 does). Case_Ignorable and Cased, which that rule needs, are read back
  from Python's own `str.lower()` by the generator, so the two agree exactly.
- **ST6:** `normalizer_normalize($s, $form = Normalizer::FORM_C)` with `FORM_C`, `FORM_D`, `FORM_KC`, `FORM_KD`
  (PHP's numbers 16, 4, 32, 8; the compiler knows the `Normalizer::` names): full decomposition from the
  table, canonical ordering, then UAX #15's composition with blocked marks; Hangul by arithmetic; ASCII returned
  as it is at once. Composition pairs are derived (a canonical pair that NFC composes back), so the exclusion
  list needs no separate file. A form that is not one of the four panics.
- **Checked:** `tools/check_unicode.py` runs every code point alone (1,112,053) and 200,000 random strings
  through all six (lower, upper, NFC, NFD, NFKC, NFKD) and compares with Python: 0 differences.
- **Size:** the tables are ~150 KB in a binary. Pin now links with `-ffunction-sections -fdata-sections` and
  dead stripping, so a program that does not call these functions does not carry them (hello: 148 KB before
  this work, 54 KB now). Benchmark times unchanged.
- Tests: `tests/strings_utf8.pn`, `tests/strings_case_norm.pn`, `tests/panics/chr_high.pn`, `substr_cut.pn`, and
  the server checks in `tests/run_tests.py` (body, path → 400; a bad header byte → U+FFFD).
- **Fresh-agent test (Sonnet, AI guide only, 2026-11-09):** a notes API with normalised unique user names, an
  optional `?int` score, Thai titles cut with `grapheme_substr`, `db_all` / `db_one` into classes, a checked
  `?string` property and `mb_strtoupper`. Two `pin check` rounds (one error: reusing a variable name with another
  type in a second `if` branch); every curl case right, including the decomposed "Café" refused as a duplicate and
  "สวัสดีค…" cut at 5 graphemes. Guide gaps it named were fixed: variables keep one type per function, `?int` can
  be promoted (the guide said it could not), a null property is still written, when to call `db_pool()`, the
  mixed-map table row, and a normalise-before-`UNIQUE` example.
