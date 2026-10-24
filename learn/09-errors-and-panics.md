# 9. Errors and panics

[Learn Pin](README.md) · previous: [8. A web API](08-web-api.md) · next: [10. Coming from PHP](10-from-php.md)

Pin has two kinds of failure:

| | when | what happens |
|---|---|---|
| **compile error** | `pin check` / `pin build` / `pin file.pn` | nothing runs; you get the line and the fix |
| **panic** | while the program runs | the program stops with `panic: ...` and exit code 1 (in a server: that request gets a 500) |

Pin's goal is to turn as many mistakes as possible into compile errors.

## Reading a compile error

```text
example.pn:3: error: $a was moved on line 2 and can no longer be used here. Use copy($a) if you need two separate values
```

File, line, what is wrong, and what to write instead. Pin stops at the first error, so fix it and check
again. Most messages name the fix; the [AI guide's error table](../ai-guide.md#errors--fixes) lists the
common ones.

## Errors as JSON

Tools and AI agents can read errors as JSON, one object per line:

```bash
pin check --json app.pn
# {"file": "app.pn", "line": 3, "severity": "error", "message": "$a was moved on line 2 ..."}
pin check --json good.pn
# {"file": "good.pn", "ok": true}
```

The exit code is 0 when the file is fine and 1 when it is not.

## PHP habits that do not compile

Pin knows the PHP features it does not have and says what to use instead:

<!-- check: error -->
```php
try {
    echo 1;
} catch (Exception $e) {
    echo 2;
}
```

Error:

```text
example.pn:1: error: try/catch is not in Pin yet (designed: pin-language/docs design/error-handling.md); check values before using them, e.g. isset($m[$k]) or $m[$k] ?? default
```

<!-- check: error -->
```php
$parts = str_split("abc");
```

Error:

```text
example.pn:1: error: unknown function str_split(): no str_split() yet: use substr($s, $i, 1) in a loop
```

## Panics

A panic is a mistake the compiler could not rule out, found while running:

| panic | how to avoid it |
|---|---|
| `index N out of range` | `isset($xs[$i])`, `$xs[$i] ?? $default`, or check `$i < count($xs)` |
| `key not found` | `isset($m[$k])` or `$m[$k] ?? $default` |
| `division by zero` | check the divisor first |
| `value is too large to allocate` | check sizes that come from input |

<!-- check: panic -->
```php
$price = ["tea" => 40];
$item = "coffee";
echo $price[$item];
```

Panic:

```text
panic: key not found on line 3 (check with isset() or use the ?? operator)
```

<!-- check: panic -->
```php
$people = 0;
echo intdiv(100, $people);
```

Panic:

```text
panic: division by zero on line 2
```

There is no `try`/`catch` yet, and a panic cannot be caught: check values before you use them. Pin never
continues with a wrong value — no `null` from a missing key, no warning and carry on.

## Writing code that does not panic

```php
function average(list<int> $xs): float {
    if (count($xs) == 0) { return 0.0; }        // guard before dividing
    $sum = 0;
    foreach ($xs as $x) { $sum += $x; }
    return $sum / count($xs);
}
function price_of(map<string,int> $menu, string $item): int {
    return $menu[$item] ?? -1;                   // -1 means "not on the menu"
}
$menu = ["tea" => 40];
echo average([]), " ", average([2, 3]), " ", price_of($menu, "tea"), " ", price_of($menu, "pizza"), "\n";
```

Output:

```text
0 2.5 40 -1
```

## In a web server

A panic inside a request handler does not stop the server. That request answers
`500 {"error":"Internal Server Error"}`, the message goes to the server's terminal, everything the request
allocated is freed, and the next request is served normally. Validate input and return 400s yourself; save
500 for real bugs.

## Try it

`$xs[$i]` panics when `$i` is out of range. Write `at(list<int> $xs, int $i, int $default): int` that never
panics, including for negative `$i`.

<details><summary>One answer</summary>

```php
function at(list<int> $xs, int $i, int $default): int {
    if ($i < 0 || $i >= count($xs)) { return $default; }
    return $xs[$i];
}
echo at([10, 20], 1, 0), " ", at([10, 20], 5, 0), " ", at([10, 20], -1, 0), "\n";
```

Output:

```text
20 0 0
```

</details>
