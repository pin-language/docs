# 10. Coming from PHP

[Learn Pin](README.md) · previous: [9. Errors and panics](09-errors-and-panics.md) · next: [11. A database](11-database.md)

## Translating a script

A PHP script that totals orders by customer:

```text
<?php
$orders = [
    ["customer" => "Ann", "amount" => 120],
    ["customer" => "Ben", "amount" => 80],
    ["customer" => "Ann", "amount" => 45],
];
$totals = [];
foreach ($orders as $o) {
    $totals[$o["customer"]] = ($totals[$o["customer"]] ?? 0) + $o["amount"];
}
arsort($totals);
foreach ($totals as $name => $sum) {
    echo "$name: $sum\n";
}
```

The Pin version. Lists of records are not there yet, so the records become two parallel lists (or a string
you `explode`); the rest maps line for line:

```php
$customers = ["Ann", "Ben", "Ann"];
$amounts = [120, 80, 45];
map<string,int> $totals = [];
foreach ($customers as $i => $c) {
    $totals[$c] += $amounts[$i];                 // a missing key starts at 0
}
// arsort: no sorting by value yet, so pick the largest each round
map<string,bool> $done = [];
for ($round = 0; $round < count($totals); $round++) {
    $best = "";
    $bestSum = -1;
    foreach ($totals as $name => $sum) {
        if (!isset($done[$name]) && $sum > $bestSum) { $best = $name; $bestSum = $sum; }
    }
    $done[$best] = true;
    echo "$best: $bestSum\n";
}
```

Output:

```text
Ann: 165
Ben: 80
```

## Checklist

| PHP | Pin |
|---|---|
| `<?php` | nothing (a leading `<?php` is ignored) |
| variables change type | one type per variable |
| `function f($x)` | `function f(int $x): int` |
| `array()`, `[]` for everything | `list<T>` or `map<K,V>`, one value type each; empty ones need the type |
| `if ($x)` truthiness | `if ($x != 0)` — conditions are `bool` |
| missing key → `null` + warning | panic; use `isset()` or `??` |
| `strpos(...) === false` | `strpos(...) < 0` |
| arrays copied on assignment | lists and maps **move**; `copy()` to duplicate |
| functions change their copy of an array | parameters are read-only; `copy()` then return the result |
| `global $x` | pass it as a parameter |
| `$_GET['x']`, `$_POST['x']` | `query_param($path, "x")`, `form_param($body, "x")` |
| `json_decode($body, true)['x']` | `json_string($body, "x")`, `json_int`, `json_float`, `json_bool`, `json_has` |
| `switch` / `match` | `if / elseif / else` |
| `try` / `catch` | check first; panics are for bugs |
| `PDO` | `db_open`, `db_exec`, `db_query`, `db_json` (SQLite; [chapter 11](11-database.md)) |
| `include`, `use`, namespaces | `import name;` and `name::fn()` ([chapter 12](12-modules-and-packages.md)) |
| Composer packages | `pin get github.com/owner/repo@v1` + `pin.lock` |
| classes, closures, `null` | not yet |
| int overflow → float | wraps around (64-bit) |
| PHP-FPM + nginx | `serve(8080, "handle")` — one native binary |

## Converting with an AI agent

Most PHP-to-Pin work can be done by an agent. Give it the [AI guide](../ai-guide.md) — the whole language
on one page — and the PHP code, and tell it to run `pin check --json` after every change. Pin's error
messages name the PHP feature and the replacement, so the agent can usually fix its own mistakes.

## Where next

- [Built-in reference](../reference/README.md) — every function with examples.
- [Language guide](../language.md) — the complete rules.
- [Examples](https://github.com/pin-language/pin/tree/HEAD/examples) — runnable programs.
- [Design notes](../design/) — classes, `null`, error handling and concurrency, as planned.
