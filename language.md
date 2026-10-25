# The Pin language guide (0.7)

Pin reads like PHP 8 and compiles to a native binary. This guide covers everything the 0.7 compiler
accepts. Anything not listed here is not supported yet.

## Files and running

A program is one `.pn` file. There is no `<?php` tag: the file is code from the first line (a leading
`<?php` is ignored, so pasted PHP still compiles). Top-level statements run in order; functions can be
declared anywhere in the file.

```bash
pin run hello.pn          # compile + run
pin build hello.pn -o hi  # native binary
pin check hello.pn        # errors only
```

## Types

| type | example | notes |
|---|---|---|
| `int` | `42`, `-7` | 64-bit; `+ - *` wrap around on overflow |
| `float` | `1.5`, `2.0e10` | 64-bit IEEE |
| `bool` | `true`, `false` | |
| `string` | `"hi $name"`, `'raw'` | bytes; Thai/UTF-8 text is kept as is |
| `list<T>` | `[1, 2, 3]`, `["a", "b"]`, `[[1], [2, 3]]` | `T` is any type except `db`, `rows`, `void` |
| `map<K,V>` | `["a" => 1]` | `K` is `int` or `string`; `V` any type except `db`, `rows`, `void`; keeps insertion order |
| a class | `new Order(1)` | see [Classes](#classes) |
| `db`, `rows` | `db_open("app.db")` | see [Database](#database-sqlite) |
| `void` | | return type only |

A variable gets its type from its first assignment and keeps it. Empty containers need the type
written out:

<!-- check: skip -->
```php
list<int> $ids = [];
map<string,int> $count = [];
$n = 0;            // int
$n = 1.5;          // compile error: assigning to $n: expected int but got float
```

## Variables must have a value on every path

<!-- check: skip -->
```php
if ($ok) { $msg = "yes"; }
echo $msg;         // compile error: $msg may be used before it is assigned ...
if ($ok) { $msg = "yes"; } else { $msg = "no"; }
echo $msg;         // fine
```

## Operators

- Arithmetic: `+ - * %`, `/` (always gives a float, like PHP), `intdiv($a, $b)` for int division.
  `%` and `intdiv` follow PHP (round toward zero). Division by zero panics.
- Compound: `+= -= *= /= %= .=`, `++`, `--`. `/=` needs a float variable.
- Comparison: `== != < <= > >= === !==` (no implicit conversions between types).
- Logic: `&& || !` — on `bool` only.
- Strings: `.` joins, `.=` appends. `"Hello $name"` and `"{$name}s"` interpolate.
- `$cond ? $a : $b`, and `$m[$k] ?? $default` / `$list[$i] ?? $default`.
- Casts: `(int)` (from float, bool or string), `(float)` (from int or string; `floatval()` does the same),
  `(string)` (from int, float or
  bool). `(int)` of a NAN, INF or out-of-range float panics. There is no `(bool)` cast — compare instead
  (`$n != 0`). From a string, `(int)`/`intval()` and `(float)`/`floatval()` read the leading number (`"2.5kg"` →
  2.5, `"abc"` → 0); an int too big for 64 bits becomes `PHP_INT_MAX` / `PHP_INT_MIN`, like PHP.
- `wrapping_add($a, $b)`, `wrapping_sub`, `wrapping_mul`: say "wrapping is intended". Today plain `+ - *`
  wrap too; once overflow checks arrive, only these will.

Conditions must be `bool`: `if ($n)` is an error, write `if ($n != 0)`.

## Control flow

`if / elseif / else`, `while`, `for`, `foreach ($xs as $x)`, `foreach ($xs as $i => $x)`,
`foreach ($map as $key => $value)`, `break`, `continue`, `return`. Braces are required.

## Functions

```php
function area(float $w, float $h): float { return $w * $h; }
function log_line(string $s): void { echo $s, "\n"; }
```

Parameter and return types are required. Recursion works. There are no default values, no named
arguments and no variadics yet.

A parameter declared with `&` may change the caller's value; the call writes `&` too:

<!-- check: skip -->
```php
function add_tax(int &$satang): void { $satang = intdiv($satang * 107, 100); }
add_tax(&$price);
```

The argument must be a variable or a path into one (`&$orders[0]`, `&$o->items`), and the other arguments of
the same call may not use it.

## Lists and maps

```php
$xs = [3, 1, 2];
$xs[] = 4;                 // append
$xs[0] = 10;               // index out of range panics
echo count($xs);
$flags = fill(100, false); // 100 copies of a value

$price = ["tea" => 40];
$price["cake"] = 89;
$price["tea"] += 5;        // a missing key starts from 0 for += -= *=
echo $price["coffee"] ?? 0;
if (isset($price["tea"])) { unset($price["tea"]); }
echo array_key_exists("tea", $price);
echo json_encode($price);  // {"cake":89}
```

Containers nest: `list<list<int>>`, `map<string,list<string>>`, `list<Order>`. Change inner values through
the path: `$grid[1][] = 4;`, `$m["a"]["b"] += 1;` (a missing key on the way panics; a missing key at the end
is created). A map has one value type; for a JSON object with mixed values use a class and `json_encode()`.

`foreach ($xs as &$x) { $x += 1; }` changes the items in place (not for bools). The `&` variable exists only
inside its loop.

## Ownership

Lists, maps, strings and objects live on the heap. Pin frees them without a garbage collector by following
these rules, all checked when you compile:

1. Each value has one owner (a variable). It is freed when the owner's function returns or the
   variable gets a new value.
2. `$b = $a;` **moves** a list, map or object: `$b` is the owner and `$a` cannot be used any more (until you
   assign it again). Use `copy($a)` for a second, independent value.
3. Strings **copy** on assignment, like PHP. String literals are never copied.
4. Passing a value to a function **lends** it read-only. The function cannot change it, move it or
   return it as is; the caller still owns it afterwards. To change it, make a copy inside, or declare the
   parameter `&` (it may then change, but still not move, the caller's value).
5. `foreach` variables are loans too.
6. While `foreach` walks over a list or map, you cannot add to it, remove from it or replace it.
7. A function that returns a list or map hands ownership to the caller.
8. Moving a value inside a loop is an error if the next round would use it again — move it after the
   loop, `copy()` it, or `break` right after moving.
9. Each `if` branch is checked on its own: moving `$a` in one branch leaves it usable in the other.
   After the `if`, `$a` counts as moved if any branch that continues moved it.
10. Reading a list, map or object out of a container or property borrows it: `$u = $users[0];` makes `$u`
    a read-only view, no copy. While `$u` is used again later in the function, `$users` cannot change.
    `copy($users[0])` gives a value of your own. A borrowed value cannot be moved, stored or returned.
11. A list, map or object inside another value cannot be moved out of it (`$all[] = $o->items;` is an
    error): copy it.

## Classes

<!-- check: skip -->
```php
class Order {
    public int $id;
    public list<string> $items = [];       // a default must be a literal
    private int $discount = 0;
    function __construct(int $id) { $this->id = $id; }
    function add(string $item): void { $this->items[] = $item; }
    function count(): int { return count($this->items); }
}
class Point { public function __construct(public int $x, public int $y) {} }   // promoted properties
$o = new Order(7);
$o->add("tea");
echo json_encode($o);                       // {"id":7,"items":["tea"]} — public properties, in order
```

- Every property has a value when the constructor ends, on every path: a default, or set in `__construct`
  (checked when compiling). Before that, `__construct` cannot read an unset property or use `$this` otherwise.
  A class without `__construct` needs a default for every property.
- `public` / `private` on properties (required) and methods (default `public`). Private members are for the
  class's own methods; `json_encode` leaves private properties out.
- Objects are values with one owner: they move on `=`, `copy()` copies deeply, parameters are read-only loans.
- A method that assigns to `$this->...` or calls such a method is a *changing method* (inferred). It can be
  called on owned variables, `&` parameters, `&` foreach variables and paths into them — not on read-only
  loans.
- Classes in modules: `export class Name`, used as `module::Name` in types and `new module::Name(...)`.
- Strings interpolate `"$o->name"` and `"{$o->items[0]->name}"`.
- Not supported: `extends`, interfaces, traits, `abstract`, `static`, `protected`, class constants,
  `readonly`, `==` on objects, and a class holding itself directly (use `list<Node>` or an id).

There are no global variables. Functions only see their parameters.

## Strings

`strlen`, `substr` (negative start/length like PHP), `strpos` (returns **-1** when not found, not
`false`), `str_contains`, `str_starts_with`, `str_ends_with`, `str_repeat`, `strtolower`, `strtoupper`
(ASCII letters only, like PHP 8.2+), `trim`, `intval` / `floatval` (leading number; too-big ints saturate at `PHP_INT_MAX` / `PHP_INT_MIN`),
`strval`.

All of these count **bytes**, like PHP: `strlen("ไทย")` is 9. Character-aware functions (`mb_*`,
`grapheme_*`) are designed but not built yet.

## Other built-ins

The [built-in reference](reference/README.md) has every function with an example and its output.

`count`, `fill($n, $value)`, `copy`, `isset($m[$k])`, `array_key_exists`, `unset($m[$k])`,
`json_encode` (int, float, bool, string, list, map), `sqrt`, `intdiv`, `echo` with several arguments.

Lists of strings: `explode($separator, $s)` gives a `list<string>` (an empty separator panics, like PHP);
`implode($glue, $list)` joins a `list<string>`, `list<int>` or `list<float>`. `sort($xs)` and `rsort($xs)`
sort a list variable you own in place (numbers by value, strings by byte order); to sort a parameter,
`copy()` it first. Changing a `list<string>` element or sorting a list is not allowed while a `foreach`
walks over it.

## Panics

A panic is a run-time error the compiler could not rule out: index out of range, missing map key,
division by zero, `intdiv(PHP_INT_MIN, -1)`, an allocation too large, `(int)` of a bad float.
It prints `panic: ...` with the line and stops the program with exit code 1. Inside
an HTTP handler it answers 500 instead and the server keeps running. A panic cannot be caught.

## Errors: throws, try, catch

<!-- check: skip -->
```php
function findUser(int $id): User throws {
    if ($id <= 0) { throw error(400, "bad id"); }
    ...
}
$u = try findUser($id);                                   // pass the error on (the function must be throws)
$u = try findUser($id) catch ($e) { return "{}"; };       // handle it: return / throw, or end with a value
$name = try nameOf($id) catch ($e) { "guest"; };
try { $a->withdraw(30); $b->deposit(30); } catch ($e) { echo $e->message; }
```

- A function or method that can fail is declared `: T throws` (a constructor: `__construct(...) throws`, and
  then `new` needs `try`). Only it may `throw` or pass errors on with a bare `try`; inside `try { } catch`
  any function may.
- Every call that can fail needs `try`: forgetting it does not compile. A `try` with nothing that can fail
  is also an error.
- One error type, `Error`, with public `$code` (int) and `$message` (string); make one with
  `error($code, $message)`. `catch ($e)`, `catch (Error $e)` and `catch (Exception $e)` are the same; one
  catch per try; no `finally`.
- Errors are returned next to the result (no stack unwinding): free when nothing fails. Ownership is checked
  on the error path too, and everything the failing code owned is freed.
- Escaping the top level: prints `error: <message> (code N)`, exit code 1. Leaving a `serve()` handler
  declared `throws`: status = code if 400–599, else 500; body `{"error":"<standard status text>"}`; the
  message goes to stderr only.

## HTTP server

<!-- check: skip -->
```php
function handle(string $method, string $path, string $body): string { ... }
serve(8080, "handle");
```

- The handler must have exactly this signature (it may add `throws`). Its return value is the response body
  (`Content-Type: application/json` unless you set another). `http_status(404)` sets the status for this response.
- `$path` includes the query string as sent. `url_path($path)` drops it; `query_param($path, "k")` reads one
  value (decoded, `""` if absent); `query_has($path, "k")` tells absent from empty. For a form body use
  `form_param($body, "k")` / `form_has($body, "k")`.
- JSON bodies: `json_has($body, "k")`, `json_string`, `json_int`, `json_float`, `json_bool` read one top-level
  key of a JSON object and return `""` / `0` / `0.0` / `false` when the key is missing, has another type, or
  the body is not a JSON object. Nested values are skipped safely; there is no full `json_decode` yet.
- Headers: `request_header("Authorization")` (case-insensitive, trimmed, `""` if absent),
  `request_has_header("X-Key")`, `response_header("Location", "/new")` (call it again for `Set-Cookie`;
  `Content-Type` replaces the default). A value with CR/LF or another control byte panics, so request data
  cannot inject headers; `Content-Length`, `Connection`, `Transfer-Encoding` and `Date` belong to the server.

## Tasks (go / await), the Hub, streams

- `$t = go f(args);` starts a task; `await $t` gives its result (`try await $t` when `f` is `throws`);
  `await_all($list)` for a `list<Task<T>>`; `try await_timeout($t, $ms)` cancels after `$ms` (504).
  `sleep_ms($ms)` waits. A task runs on the thread that started it; tasks take turns, so there are no data
  races.
- Rules (checked when compiling): every task is awaited before the function that started it returns; a task
  borrows its arguments until then (they cannot change); `go f(&$x)` lends `$x` exclusively until the await;
  `Task<T>` only in local variables and lists. `go` starts your functions (not built-ins, not methods).
- On an error or panic exit, unawaited tasks are waited for (and freed) before the function's values go.
  Cancelling is cooperative: a cancelled task's waits end at once.
- In a server every request is a task: a handler that waits does not block other requests.
- Hub: `hub_publish`, `hub_subscribe`, `hub_resume`, `hub_next($s, $ms)` (time limit required; 504 / 507 /
  499), `hub_last_id`. Server-Sent Events from a handler: `sse_start`, `sse_send`, `sse_send_id`, `sse_comment`.
- Other servers and programs: `http_get`, `http_post`, `http_stream` + `stream_next` / `stream_last_id`
  (http:// only), `run($program, $args, $ms)` (no shell). See [Learn chapter 14](learn/14-tasks-and-realtime.md).

## Modules and packages

Each `.pn` file is a module. `import prices;` loads `prices.pn` from the project folder (the main file's
folder; inside a package, the package's root), whichever file contains the import (`import util/text;` loads
`util/text.pn`; `import util/text as t;` renames it); call its functions as
`prices::price(...)`. Only functions and classes marked `export` can be used from other files. Imported files
may contain only functions, classes and imports (no top-level code), and imports may not form a circle. All files compile
into one binary.

Packages are Git repositories: `pin get github.com/owner/repo@v1.0.0` writes the commit and a SHA-256 of the
package's `.pn` files to `pin.lock`; `import github.com/owner/repo/module;` then uses it. The hash is checked on
every build, so changed package code stops the build. See
[Learn chapter 12](learn/12-modules-and-packages.md).

## Database (SQLite)

`db_open($path)` gives a `db`; `db_exec`, `db_query` (→ `rows`, read with `db_next` and `db_int` /
`db_float` / `db_string` / `db_is_null`) and `db_json` run SQL. The SQL must be a string literal and values
go in `?` placeholders, so SQL injection cannot compile. `db` and `rows` are owned values: they close when
they go out of scope (also when a handler panics), move on `=`, and are lent to functions. Constraint
violations make `db_exec` return -1 (`db_error` explains); other SQL errors panic. Details:
[reference/database.md](reference/database.md). On Linux, building a program that uses the database needs
SQLite's development files (`sudo apt install libsqlite3-dev`).
- One thread per CPU core (`PN_THREADS=n` to change). Keep-alive and pipelining are supported.
- Limits: 64 KB of headers (431), 64 MB of body (413). A request must arrive completely within 15 s of its
  first byte (408; a new connection must send its first request in that time too), an idle keep-alive
  connection closes after 60 s, an unread response after 30 s, and at most 10 000 connections are open (503).
  Change them with `PN_READ_TIMEOUT_MS`, `PN_IDLE_TIMEOUT_MS`, `PN_WRITE_TIMEOUT_MS`, `PN_MAX_CONNS`.
- `Transfer-Encoding` (chunked bodies) is refused with 501, and a `Content-Length` that is not plain digits or
  appears twice with different values gets 400, so requests cannot be smuggled past a proxy.
- No TLS and no HTTP/2, by design ([design/tls.md](design/tls.md)): a proxy does https in both directions —
  incoming in front of `serve()`, outgoing for `http_get` & co. With Caddy:

```text
# Caddyfile
api.example.com {                       # incoming: https for the world, plain http to Pin
	reverse_proxy 127.0.0.1:8080 {
		flush_interval -1               # pass Server-Sent Events through at once
	}
}

http://127.0.0.1:9001 {                 # outgoing: Pin calls http://127.0.0.1:9001/v1/...
	bind 127.0.0.1                      # only this machine: otherwise it is an open proxy
	reverse_proxy https://api.anthropic.com {
		header_up Host {upstream_hostport}
		flush_interval -1
	}
}
```

  Headers such as `Authorization` pass through unchanged. (Config written from Caddy's documentation; adjust
  names and ports.)

## Not in Pin yet

Inheritance and interfaces, `null` and `?Type`, `finally`, default parameter values,
closures, sorting with a custom comparison, a full `json_decode`
(nested objects and arrays), databases other than SQLite (PostgreSQL is next), WebSocket. Designs for most of these are in
[`design/`](design/).
