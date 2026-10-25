# Writing Pin — guide for AI coding agents

Pin 0.6. Give this file to the agent, or point it at the raw URL:
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
  `prices::price($x)`. Only `export function ...` / `export class ...` can be used from another file
  (`new prices::Item(...)`, type `prices::Item`). Imported files contain only functions, classes and imports.
  `import util/text as t;` for folders and short names.

## The rules that matter

1. **Types.** `int float bool string list<T> map<K,V> void`, plus your classes. `K` ∈ int/string; `T` and `V`
   can be any type, nested: `list<Order>`, `list<list<int>>`, `map<string,list<string>>`, `map<int,User>`.
2. **Every parameter and return type is written.** `function f(int $n, list<int> $xs): string`.
3. **A variable keeps the type of its first value.** Empty containers need the type:
   `list<int> $ids = [];` `map<string,int> $count = [];`
4. **Conditions are bool.** `if ($n != 0)`, `if (count($xs) > 0)`, `if (strlen($s) > 0)` — never `if ($n)`.
5. **A variable must have a value on every path before use.** Initialise before `if` / loops.
6. **Lists, maps and objects move on `=`.** After `$b = $a;` do not use `$a`. Want two? `$b = copy($a);`
7. **Parameters are read-only loans.** To change the caller's value, declare `&` and write `&` at the call
   too: `function discount(Order &$o): void {...}` … `discount(&$order);`. Otherwise copy:
   `$out = copy($xs);` then change `$out` and `return $out;`.
8. **Do not add to / remove from / replace a list or map inside a `foreach` over it.** Collect changes in
   another variable, apply after the loop.
9. **Strings copy on `=`** (PHP-like). Join with `.`; `+` on strings is an error.
10. **No globals.** Pass everything as parameters. Functions may be declared anywhere in the file.
11. **Non-void functions must return on every path.**
12. **Missing map key / bad index panic.** Use `isset($m[$k])` or `$m[$k] ?? $default`. Panics are bugs and
    cannot be caught; expected failures use `throws` / `try` (below).
13. **A map literal has one value type.** `["a" => 1, "b" => 2.5]` becomes `map<string,float>`;
    `["a" => 1, "b" => "x"]` is an error — for a JSON object with mixed values, use a class and
    `json_encode($obj)` (see Classes).
14. **Both sides of `?:` and `??` have the same type.** `$n < 10 ? "0" . $n : strval($n)`, not `... : $n`.
15. **`unset()` works on maps only.** To drop items from a list, build a new list without them.
16. **`/` always gives a float** — for list indexes and counts use `intdiv($a, $b)`.
17. **Numbers from text never fail.** `intval("abc")` is 0; a number too big for an int becomes
    `PHP_INT_MAX` / `PHP_INT_MIN` (like PHP), so your range check rejects it. `floatval("2.5kg")` and
    `(float)"2.5"` read the leading number. Always range-check numbers that come from a request.

## Errors: throws / try / catch

```php
class User { public function __construct(public int $id, public string $name) {} }

function findUser(int $id): User throws {               // can fail: `throws` after the return type
    if ($id <= 0) { throw error(400, "bad id $id"); }   // error(int $code, string $message)
    if ($id > 100) { throw error(404, "user $id not found"); }
    return new User($id, "user$id");
}

function nameOf(int $id): string throws {
    $u = try findUser($id);                 // pass the error on: allowed only in a `throws` function
    return $u->name;
}

$name = try nameOf(500) catch ($e) { "guest"; };        // handle: the block ends with the value to use
try {                                                     // several lines, PHP style
    echo nameOf(7), "\n";
    echo nameOf(-1), "\n";                               // fails: goes to catch
} catch ($e) {
    echo "failed ", $e->code, ": ", $e->message, "\n";   // failed 400: bad id -1
}
$u = try findUser(0) catch ($e) { return; };            // ...or the block returns / throws
```

- **Every call to a `throws` function or method needs `try`** — also as a statement: `try $from->withdraw($n);`.
  A constructor that can fail is `function __construct(int $start) throws { ... }`; then `try new Account(5)`.
  Inside `try { ... } catch` the calls need no `try`.
- A route that matches nothing in a `throws` handler: `throw error(404, "no route $route");`.
- One error type `Error` (`$e->code`, `$e->message`, `json_encode($e)`); `catch ($e)` / `catch (Error $e)` /
  `catch (Exception $e)` all work; one catch, no `finally`.
- Panics (bad index, missing key, division by zero) are not errors and are not caught.
- An error escaping the top level prints `error: message (code N)` and exits 1.
- A `serve()` handler may be `: string throws`: an escaping error answers its code (400–599, else 500) with
  `{"error":"Not Found"}`-style standard text, without the headers set before it; the message goes only to
  the log. For a custom error body, catch it and return your own JSON with `http_status()`.

## Classes

```php
class Item {
    public function __construct(public string $name, public int $price) {}   // promoted: declares + sets
}

class Order {
    public int $id;
    public list<Item> $items = [];          // defaults are literals: 0, "", false, [], [1, 2]
    private int $discount = 0;              // private: only Order's methods; left out of json_encode

    function __construct(int $id) { $this->id = $id; }      // must set every property without a default

    function add(string $name, int $price): void { $this->items[] = new Item($name, $price); }

    function total(): int {
        $t = 0;
        foreach ($this->items as $it) { $t += $it->price; }
        return $t - $this->discount;
    }
}

$o = new Order(1);
$o->add("tea", 40);
$o->items[0]->price = 35;                   // change through a path
echo $o->total(), "\n";
echo json_encode($o), "\n";               // {"id":1,"items":[{"name":"tea","price":35}]}
```

- Objects are **values with one owner**, like lists: `$b = $a;` moves, `copy($a)` makes a separate one, a
  parameter `Order $o` is read-only, `Order &$o` (called with `&$order`) may change it.
- A method that assigns `$this->...` (or calls such a method) is a **changing method**. You can call it on
  your own variables, `&` parameters, `foreach (... as &$x)` items and paths into them — not on read-only
  parameters or plain `foreach` variables.
- `$u = $users[0];` (an object, list or map read from a list, map or property) **borrows** it read-only, no
  copy. While `$u` is still used later, `$users` cannot be changed. Need your own? `$u = copy($users[0]);`
- Change items in place: `foreach ($users as &$u) { $u->visits += 1; }`
- No inheritance, interfaces, static members, `null` or `?->` yet. A class cannot hold itself (use
  `list<Node>` or an id). `==` does not compare objects: compare properties.
- Promote only `int float bool string` constructor parameters. For a list, map or object property, declare it
  (`public list<int> $scores = [];`) and set it with `$this->scores = copy($scores);` in `__construct`.
- `&` also takes paths: `drop_lowest(&$students[1])`, `f(&$o->items)`.
- `json_encode` writes public properties in declaration order (promoted ones sit where `__construct` is in the
  class body); objects, lists of objects and maps of objects all work. Strings: `"{$o->name}"`, `"$o->name"`, `"{$o->items[0]->name}"`.

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

// mixed JSON object: a class, then json_encode()
class UserOut {
    public function __construct(public int $id, public string $name, public bool $admin) {}
}
function user_json(int $id, string $name): string {
    return json_encode(new UserOut($id, $name, false));     // {"id":7,"name":"Ann","admin":false}
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
function handle(string $method, string $path, string $body): string {   // exactly this signature (`throws` allowed)
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

Headers: `request_header("Authorization")` → string (`""` if absent; name case-insensitive),
`request_has_header("X-Api-Key")` → bool, `response_header("Location", "/orders/7")` (repeat for several
`Set-Cookie`; `response_header("Content-Type", "text/html; charset=utf-8")` replaces the default
`application/json`). A header value containing CR/LF panics (no header injection) — that is a 500 the client caused, so when a
value comes from the request, check it first and answer 400 (`str_contains($v, "\r")`, `"\n"`); `Content-Length`,
`Connection`, `Transfer-Encoding`, `Date` are set by the server. Handlers cannot keep state between requests
(no globals): compute each answer from the request.

The server closes slow or idle clients by itself (408 / idle close / 503 over 10 000 connections; tune with
`PN_READ_TIMEOUT_MS`, `PN_IDLE_TIMEOUT_MS`, `PN_WRITE_TIMEOUT_MS`, `PN_MAX_CONNS`). No TLS: use a reverse proxy.

## PHP → Pin

| PHP | Pin |
|---|---|
| `array(1, 2)`, `[]` untyped | `[1, 2]`, `list<int> $a = [];` |
| `$a = ["x" => 1, "y" => "s"]` (mixed) | one value type per map; build JSON strings for mixed objects |
| `null`, `?int` | not yet — use `-1`, `""`, empty list, or a separate `bool` |
| `class`, `new`, `->`, `$this` | the same; no `extends` / `interface` / `static`; objects move on `=` |
| `function f(array &$a)`, `f($a)` | `function f(list<int> &$a)`, `f(&$a)` — `&` at the call too |
| `throw new InvalidArgumentException("x")` | `throw error(400, "x");` in a function declared `: T throws` |
| `try { ... } catch (Exception $e) { ... } finally` | the same without `finally`; calls outside it need `try f()` |
| `switch`, `match` | `if / elseif / else` |
| `function () {}`, `fn() =>` | named functions |
| `include`, `use`, `namespace` | `import prices;` (loads prices.pn from the project folder) and `prices::fn()`; mark callable functions `export` |
| Composer packages | `pin get github.com/owner/repo@v1.0.0`, then `import github.com/owner/repo/module;` |
| `global`, `static`, `const`, `define` | parameters / local variables |
| `strpos(...) === false` | `strpos(...) < 0` |
| `explode`, `implode`, `sort`, `rsort` | the same (`sort($xs)` needs a list variable you own) |
| `array_map`, `in_array`, `max`, `sprintf`, `usort`… | write the loop; the error message names the replacement |
| `$_SERVER["HTTP_AUTHORIZATION"]`, `getallheaders()` | `request_header("Authorization")` |
| `header("Location: /x")`, `setcookie(...)` | `response_header("Location", "/x")`, `response_header("Set-Cookie", "...")` |
| `$_GET["x"]`, `$_POST["x"]` | `query_param($path, "x")`, `form_param($body, "x")` |
| `new PDO(...)`, `$stmt->execute([...])`, `fetch()` | `db_open`, `db_exec` / `db_query` + `db_next`, or `db_json` for a JSON array |
| `json_decode($body, true)["x"]` | `json_string($body, "x")` / `json_int` / `json_float` / `json_bool` / `json_has` (top level only) |
| `(bool)$x`, truthiness | compare explicitly |
| `$s + 1` on strings | `intval($s) + 1` |
| `list($a, $b) = ...` | assign separately |
| `foreach ($xs as &$x)` | the same (not for bools); the `&` variable is gone after the loop |
| default parameter values `int $n = 1` | not yet — pass every argument |

## Built-ins (complete list)

<!-- builtins:start (generated by tools/gen_docs.py in the pin repo) -->
`strlen substr strpos str_contains str_starts_with str_ends_with str_repeat strtolower strtoupper trim explode implode count fill copy sort rsort isset array_key_exists unset intdiv sqrt wrapping_add wrapping_sub wrapping_mul intval floatval strval json_encode json_has json_string json_int json_float json_bool serve http_status request_header request_has_header response_header url_path query_param query_has form_param form_has db_open db_exec db_query db_next db_int db_float db_string db_is_null db_json db_last_id db_error error` · constants `PHP_EOL PHP_INT_MAX PHP_INT_MIN` · casts `(int)` from float/bool/string, `(float)` from int/string, `(string)` from int/float/bool. Details and examples for each: https://github.com/pin-language/docs/blob/HEAD/reference/README.md
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
| `is a parameter lent to this function read-only` | declare `T &$p` and call with `&$x`, or `$copy = copy($p);` |
| `can change its argument $x, so write f(&$x)` | add `&` at the call |
| `borrows from it and is used again on line N` | finish using the borrowed variable first, or `copy()` it |
| `is borrowed (read-only) from another value` | change the original path (`$users[$i]->x = ...`) |
| `belongs to the value it is part of and cannot be moved out` | `copy($o->items)` |
| `does not set $this->x on every path` | set it in `__construct` in every branch, or give a default |
| `has no __construct(), so every property needs a default` | add defaults, or a `__construct` |
| `is a foreach variable lent read-only` | `foreach (... as &$x)` |
| `cannot store $x inside itself` | store `copy($x)` |
| `while a foreach is looping over it` | collect into another list/map, apply after the loop |
| `an empty [] needs a type` | `list<int> $a = [];` / `map<string,int> $m = [];` |
| `condition must be bool` | write the comparison: `$n != 0` |
| `expected int but got float` | the variable is int: use a new variable, `(int)`, or start it as `0.0` |
| `cannot combine string and int` | join with `.`; convert with `intval()` / `strval()` |
| `can reach its end without returning` | add a final `return` |
| `X::f() is not exported` | add `export` before `function f` in that file |
| there is no `import X;` in this file | add `import X;` at the top (each file lists its own imports) |
| `import X: there is no file X.pn in the project folder` | import paths start at the main file's folder: `import dir/file;` |
| `f() can fail. Write try f(...)` | `try f()` in a `throws` function, or `try f() catch ($e) { ...; value; }` |
| `is not declared throws, so try cannot pass the error on` | add `throws` after the return type, or use catch |
| `this catch block must return, throw, or end with a value` | end the block with a value: `0;` / `"";` |
| `nothing after this try can fail` | remove `try` (the function is not `throws`) |
| `may only contain functions, classes and imports` | move top-level code from the imported file into a function or the main file |
| `import cycle: a.pn -> b.pn -> a.pn` | move what both need into a third file that both import |
| `is not in pin.lock. Run: pin get ...` | run that `pin get` with a version, e.g. `@v1.0.0` |
| `does not match pin.lock` | delete the package's cache folder named in the message; never just re-run `pin get` |
| `both sides of ?: / ?? must have the same type` | convert one side with `strval()` / `intval()` / `(float)` |
| `list index must be int but got float` | use `intdiv($a, $b)` instead of `/` |
| `unset() works on maps` | build a new list without the items |
| `… is not in Pin yet` | use the replacement in the message / the table above |
| run time `panic: key not found` | `isset($m[$k])` or `$m[$k] ?? default` |
| run time `panic: index N out of range` | check `$i < count($xs)` |
