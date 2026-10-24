# Writing Pin — guide for AI coding agents

Pin 0.4. Give this file to the agent, or point it at the raw URL:
`https://raw.githubusercontent.com/pin-language/docs/HEAD/ai-guide.md`. It is complete for this version: if a feature is not
in this file, Pin does not have it yet. Pin looks like PHP 8 but is statically typed and has no garbage
collector, so a lot of PHP habits do not compile. The compiler explains each error and the fix.

## Loop

```bash
pin check --json app.pn   # one JSON line per error: {"file","line","severity","message"}; {"file","ok":true} if clean
pin run app.pn            # compile and run
pin build app.pn -o app   # native binary
```

Write → `pin check --json` → fix the reported line → repeat → `pin run`. Errors stop at the first one,
so fix and re-check. Exit code 0 = ok, 1 = compile error or run-time panic, 2 = toolchain problem.

## Program shape and output

- A program is one `.pn` file. Do not write `<?php` (it is ignored if present). Statements outside functions run from top
  to bottom; functions can be declared anywhere in the file (before or after use).
- Top-level variables are local to the top level: functions cannot see them (there are no globals).
- Print with `echo`, several values separated by commas: `echo "total: ", $t, "\n";`. Double-quoted
  strings interpolate `"$name"` and `"{$name}x"`; single-quoted strings do not. `PHP_EOL` is `"\n"`.
- Printing a float uses PHP's format: `380.5` → `380.5`, `380.0` → `380`, `1/3` → `0.33333333333333`.
  `json_encode` of a whole float keeps `.0` (`380.0`; PHP would print `380`). `true` prints `1`, `false` prints nothing.
- Maps keep insertion order (like PHP arrays), in `foreach` and in `json_encode`.

- Split a big program into files: `import prices;` loads `prices.pn` from the project folder (where the main
  file is — the same path from every file, no `../`); call
  `prices::price($x)`. Only `export function ...` can be called from another file. Imported files contain only
  functions and imports. `import util/text as t;` for folders and short names.

## The rules that matter

1. **Types.** `int float bool string list<T> map<K,V> void`. `T` ∈ int/float/bool/string. `K` ∈ int/string,
   `V` ∈ int/float/bool/string. No nesting (`list<list<int>>`, a map of lists: no).
2. **Every parameter and return type is written.** `function f(int $n, list<int> $xs): string`.
3. **A variable keeps the type of its first value.** Empty containers need the type:
   `list<int> $ids = [];` `map<string,int> $count = [];`
4. **Conditions are bool.** `if ($n != 0)`, `if (count($xs) > 0)`, `if (strlen($s) > 0)` — never `if ($n)`.
5. **A variable must have a value on every path before use.** Initialise before `if` / loops.
6. **Lists and maps move on `=`.** After `$b = $a;` do not use `$a`. Want two? `$b = copy($a);`
7. **Parameters are read-only loans.** Do not change, move or return a list/map parameter; copy it:
   `$out = copy($xs);` then change `$out` and `return $out;`.
8. **Do not add to / remove from / replace a list or map inside a `foreach` over it.** Collect changes in
   another variable, apply after the loop.
9. **Strings copy on `=`** (PHP-like). Join with `.`; `+` on strings is an error.
10. **No globals.** Pass everything as parameters. Functions may be declared anywhere in the file.
11. **Non-void functions must return on every path.**
12. **Missing map key / bad index panic.** Use `isset($m[$k])` or `$m[$k] ?? $default`.
13. **A map literal has one value type.** `["a" => 1, "b" => 2.5]` becomes `map<string,float>`;
    `["a" => 1, "b" => "x"]` is an error — build mixed JSON objects as strings (idiom below).
14. **Both sides of `?:` and `??` have the same type.** `$n < 10 ? "0" . $n : strval($n)`, not `... : $n`.
15. **`unset()` works on maps only.** To drop items from a list, build a new list without them.
16. **`/` always gives a float** — for list indexes and counts use `intdiv($a, $b)`.
17. **Numbers from text never fail.** `intval("abc")` is 0; a number too big for an int becomes
    `PHP_INT_MAX` / `PHP_INT_MIN` (like PHP), so your range check rejects it. `floatval("2.5kg")` and
    `(float)"2.5"` read the leading number. Always range-check numbers that come from a request.

## Idioms

```php
// build and return a list (caller owns it)
function evens(int $n): list<int> {
    list<int> $out = [];
    for ($i = 0; $i < $n; $i++) { if ($i % 2 == 0) { $out[] = $i; } }
    return $out;
}

// read a list without copying
function sum(list<int> $xs): int {
    $t = 0;
    foreach ($xs as $x) { $t += $x; }
    return $t;
}

// "modify" a parameter: copy, change, return
function bump(list<int> $xs): list<int> {
    $out = copy($xs);
    for ($i = 0; $i < count($out); $i++) { $out[$i] += 1; }
    return $out;
}

// counting with a map (a missing key starts at 0 for += -= *= ++ --)
function tally(list<int> $xs): map<int,int> {
    map<int,int> $c = [];
    foreach ($xs as $x) { $c[$x] += 1; }
    return $c;
}

// "not found" without null: return -1 / "" and check it
function find(list<int> $xs, int $want): int {
    foreach ($xs as $i => $x) { if ($x == $want) { return $i; } }
    return -1;
}

// mixed JSON object: build the string; json_encode() a string to quote/escape it
function user_json(int $id, string $name): string {
    return "{\"id\":" . $id . ",\"name\":" . json_encode($name) . "}";
}
```

Sorting: `sort($xs)` / `rsort($xs)` sort a list variable you own, in place (ints, floats, bools, or strings
by byte order). A parameter is a loan, so copy it first.

```php
function median(list<int> $xs): float {     // assumes count($xs) > 0
    $s = copy($xs);
    sort($s);
    $n = count($s);
    $mid = intdiv($n, 2);
    return $n % 2 == 1 ? (float)$s[$mid] : ($s[$mid - 1] + $s[$mid]) / 2;
}
```

Money: keep integer satang/cents; format with `intdiv` and `%` (no `sprintf` / `number_format` yet).

```php
function baht(int $satang): string {        // 123450 -> "1234.50", -5 -> "-0.05"
    $sign = $satang < 0 ? "-" : "";
    $abs = $satang < 0 ? -$satang : $satang;
    $frac = $abs % 100;
    return $sign . intdiv($abs, 100) . "." . ($frac < 10 ? "0" . $frac : strval($frac));
}
```

Top N from a map by value (`sort` has no custom comparison yet): pick the best not yet used, N times.

```php
function top3(map<string,int> $counts): string {
    map<string,bool> $used = [];
    $out = "";
    for ($round = 0; $round < 3; $round++) {
        $best = "";
        $bestN = -1;
        foreach ($counts as $w => $n) {
            if (!isset($used[$w]) && $n > $bestN) { $best = $w; $bestN = $n; }
        }
        if ($bestN < 0) { break; }
        $used[$best] = true;
        $out .= "$best: $bestN\n";
    }
    return $out;
}
```

Strings in lists: `explode`, `implode`, `list<string>`.

```php
function count_words(string $text): map<string,int> {
    map<string,int> $counts = [];
    foreach (explode(" ", $text) as $w) {          // explode($separator, $string) like PHP
        if (strlen($w) > 0) { $counts[strtolower($w)] += 1; }
    }
    return $counts;
}

function initials(list<string> $names): string {
    list<string> $out = [];
    foreach ($names as $n) { $out[] = strtoupper(substr($n, 0, 1)); }
    sort($out);
    return implode(",", $out);                     // implode works on list<string|int|float>
}
```

HTTP API — GET with a query string, POST with a JSON or form body:

```php
function handle(string $method, string $path, string $body): string {   // exactly this signature
    $route = url_path($path);                       // "/quote?item=cake" -> "/quote"
    if ($method == "GET" && $route == "/health") { return "{\"ok\":true}"; }
    if ($method == "GET" && $route == "/quote") {
        $item = query_param($path, "item");         // "" when missing; %XX and + are decoded
        $qty = intval(query_param($path, "qty"));
        if ($item == "" || $qty < 1 || $qty > 20) { http_status(400); return "{\"error\":\"item and qty 1-20\"}"; }
        return "{\"item\":" . json_encode($item) . ",\"qty\":" . $qty . "}";
    }
    if ($method == "POST" && $route == "/orders") {
        // body {"item":"cake","qty":2} — top-level keys only
        if (!json_has($body, "item")) { http_status(400); return "{\"error\":\"item is required\"}"; }
        $item = json_string($body, "item");         // "" if missing or not a string
        $qty = json_int($body, "qty");              // 0 if missing or not an integer
        return "{\"created\":" . json_encode($item) . ",\"qty\":" . $qty . "}";
    }
    http_status(404);
    return "{\"error\":\"not found\"}";
}
serve(8080, "handle");    // last statement; blocks forever
```

Request helpers (all take strings and never fail on bad input):
- `url_path($path)` — the path without `?query`.
- `query_param($path, "key")`, `form_param($body, "key")` — the decoded value, `""` if absent.
- `json_has($body, "key")` — bool. `json_string` → string (`""`), `json_int` → int (`0`), `json_float` →
  float (`0.0`), `json_bool` → bool (`false`), with the default when the key is missing, has another type, or
  the body is not a JSON object. Only top-level keys of an object are read; nested objects and arrays are
  skipped safely. `json_int` of a number too big for an int gives `PHP_INT_MAX` / `PHP_INT_MIN`, like `intval`.
- `query_has($path, "key")` / `form_has($body, "key")` tell "missing" from "present but empty" (`?limit=`).

Database (SQLite) — one connection per request, closed automatically:

```php
function handle(string $method, string $path, string $body): string {
    $db = db_open("shop.db");
    db_exec($db, "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, item TEXT NOT NULL, qty INTEGER NOT NULL)", []);
    if ($method == "POST" && url_path($path) == "/orders") {
        $n = db_exec($db, "INSERT INTO orders (item, qty) VALUES (?, ?)", [json_string($body, "item"), strval(json_int($body, "qty"))]);
        if ($n < 0) { http_status(409); return json_encode(["error" => db_error($db)]); }
        http_status(201);
        return "{\"id\":" . db_last_id($db) . "}";
    }
    return db_json($db, "SELECT id, item, qty FROM orders ORDER BY id", []);   // a JSON array of objects
}
serve(8080, "handle");
```

- **The SQL must be a string literal**; values go in `?` placeholders and the list (`list<string>` is
  simplest — SQLite converts `"2"` for INTEGER columns). Building SQL from variables does not compile.
- `db_exec` returns rows changed, or -1 when a constraint refuses (`db_error($db)` says which); bad SQL panics.
- Row by row: `$r = db_query(...); while (db_next($r)) { db_int($r, "qty"); db_string($r, "item"); }`.
  NULL reads as 0 / `""`; check with `db_is_null`.
- Every `db_*` function: [reference/database.md](https://github.com/pin-language/docs/blob/HEAD/reference/database.md).

The response is always `Content-Type: application/json`; the body format is yours. There is no header
access yet. Handlers cannot keep state between requests (no globals): compute each
answer from the request.

## PHP → Pin

| PHP | Pin |
|---|---|
| `array(1, 2)`, `[]` untyped | `[1, 2]`, `list<int> $a = [];` |
| `$a = ["x" => 1, "y" => "s"]` (mixed) | one value type per map; build JSON strings for mixed objects |
| `null`, `?int` | not yet — use `-1`, `""`, empty list, or a separate `bool` |
| `class`, `new`, `->` | not yet — functions + maps |
| `try`/`catch`/`throw` | not yet — check first (`isset`, `??`, range checks) |
| `switch`, `match` | `if / elseif / else` |
| `function () {}`, `fn() =>` | named functions |
| `include`, `use`, `namespace` | `import prices;` (loads prices.pn from the project folder) and `prices::fn()`; mark callable functions `export` |
| Composer packages | `pin get github.com/owner/repo@v1.0.0`, then `import github.com/owner/repo/module;` |
| `global`, `static`, `const`, `define` | parameters / local variables |
| `strpos(...) === false` | `strpos(...) < 0` |
| `explode`, `implode`, `sort`, `rsort` | the same (`sort($xs)` needs a list variable you own) |
| `array_map`, `in_array`, `max`, `sprintf`, `usort`… | write the loop; the error message names the replacement |
| `$_GET["x"]`, `$_POST["x"]` | `query_param($path, "x")`, `form_param($body, "x")` |
| `new PDO(...)`, `$stmt->execute([...])`, `fetch()` | `db_open`, `db_exec` / `db_query` + `db_next`, or `db_json` for a JSON array |
| `json_decode($body, true)["x"]` | `json_string($body, "x")` / `json_int` / `json_float` / `json_bool` / `json_has` (top level only) |
| `(bool)$x`, truthiness | compare explicitly |
| `$s + 1` on strings | `intval($s) + 1` |
| `list($a, $b) = ...` | assign separately |
| `foreach ($xs as &$x)` | `for ($i = 0; $i < count($xs); $i++) { $xs[$i] ... }` |

## Built-ins (complete list)

<!-- builtins:start (generated by tools/gen_docs.py in the pin repo) -->
`strlen substr strpos str_contains str_starts_with str_ends_with str_repeat strtolower strtoupper trim explode implode count fill copy sort rsort isset array_key_exists unset intdiv sqrt wrapping_add wrapping_sub wrapping_mul intval floatval strval json_encode json_has json_string json_int json_float json_bool serve http_status url_path query_param query_has form_param form_has db_open db_exec db_query db_next db_int db_float db_string db_is_null db_json db_last_id db_error` · constants `PHP_EOL PHP_INT_MAX PHP_INT_MIN` · casts `(int)` from float/bool/string, `(float)` from int/string, `(string)` from int/float/bool. Details and examples for each: https://github.com/pin-language/docs/blob/HEAD/reference/README.md
<!-- builtins:end -->

String functions count bytes (`strlen("ไทย")` is 9). `/` always gives a float; use `intdiv($a, $b)`.
Ints wrap around on overflow.

## Errors → fixes

| message contains | fix |
|---|---|
| `was moved on line N` | use `copy($x)` at line N, or stop using the old name |
| `may have been moved on line N (on one path…)` | copy in that branch, or reassign after the `if` |
| `is moved inside a loop` | move after the loop, `copy()`, or `break` right after the move |
| `may be used before it is assigned` | give it a value before the `if`/loop |
| `is a parameter lent to this code, so it cannot be changed` | `$copy = copy($p);` and work on `$copy` |
| `while a foreach is looping over it` | collect into another list/map, apply after the loop |
| `an empty [] needs a type` | `list<int> $a = [];` / `map<string,int> $m = [];` |
| `condition must be bool` | write the comparison: `$n != 0` |
| `expected int but got float` | the variable is int: use a new variable, `(int)`, or start it as `0.0` |
| `cannot combine string and int` | join with `.`; convert with `intval()` / `strval()` |
| `can reach its end without returning` | add a final `return` |
| `X::f() is not exported` | add `export` before `function f` in that file |
| there is no `import X;` in this file | add `import X;` at the top (each file lists its own imports) |
| `import X: there is no file X.pn in the project folder` | import paths start at the main file's folder: `import dir/file;` |
| `may only contain functions and imports` | move top-level code from the imported file into a function or the main file |
| `import cycle: a.pn -> b.pn -> a.pn` | move what both need into a third file that both import |
| `is not in pin.lock. Run: pin get ...` | run that `pin get` with a version, e.g. `@v1.0.0` |
| `does not match pin.lock` | delete the package's cache folder named in the message; never just re-run `pin get` |
| `both sides of ?: / ?? must have the same type` | convert one side with `strval()` / `intval()` / `(float)` |
| `list index must be int but got float` | use `intdiv($a, $b)` instead of `/` |
| `unset() works on maps` | build a new list without the items |
| `… is not in Pin yet` | use the replacement in the message / the table above |
| run time `panic: key not found` | `isset($m[$k])` or `$m[$k] ?? default` |
| run time `panic: index N out of range` | check `$i < count($xs)` |
