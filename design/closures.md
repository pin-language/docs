# Pin — Closures

**Status (2026-11-09):** steps 1–2 **built** (the owner took the proposed answers to Q1–Q3): `fn` types, named
functions as values, local closures. Steps 3 (`use (&$x)`) and 4 (escaping closures) are compile errors that say
so. See "As built" at the end.

Decision rule: memory safety > speed > clarity > looking like PHP.

## What it looks like

```php
// the common case: a closure written where it is used (no types needed, nothing copied)
$cheap  = array_filter($items, fn($i) => $i->price < $limit);       // $limit is read, not copied
$labels = array_map(fn($i) => $i->name . " " . number_format($i->price / 100, 2), $items);
usort($items, fn($a, $b) => $b->price <=> $a->price);

// your own functions can take one: its type says what it gets and gives
function total(list<Item> $items, fn(Item): int $price): int {
    $t = 0;
    foreach ($items as $i) { $t += $price($i); }
    return $t;
}
echo total($items, fn($i) => $i->price * $i->qty);

// a function that makes a function: the closure owns what it keeps
function discounter(int $percent): fn(int): int {
    return fn($price) => intdiv($price * (100 - $percent), 100);
}
$tenOff = discounter(10);
echo $tenOff(4500);                       // 4050
```

## Why this shape

A closure is a function plus the values it uses from around it (its *captures*). In PHP every closure is a
heap object holding copies (or references) of those values, and the garbage collector frees it. Pin has no
garbage collector and lets nothing point at a value except its one owner or a loan checked at compile time, so
the question is only: **who owns the captures, and how long may the closure live?**

Most closures in PHP code are written at the call that uses them (`array_map`, `usort`, `array_filter`, a
callback parameter) and never outlive that call. Swift makes closure parameters *non-escaping* by default for
the same reason (a closure that cannot escape may borrow, and costs nothing); Rust distinguishes closures that
borrow from those that own (`move`). Pin follows that split, with the cheap case as the default.

## Rules

### C1 — `fn` types
`fn(T1, T2): R` is a type, written like the rest of Pin's types: `fn(Item): int`, `fn(int, int): bool`,
`fn(string): void`, `fn(Req): Res throws`. A parameter, variable, return value or property can have it.
Calling one is PHP's syntax: `$f($x)`. Two `fn` types are the same when their parameters, result and `throws`
are; there is no conversion between different ones.

### C2 — named functions are values too
`by_price(...)` (PHP 8.1's first-class callable syntax) gives the function `by_price` as an `fn` value with
nothing captured. The string forms `usort($xs, "by_price")` keep working; new code uses `by_price(...)`.

### C3 — a closure's parameter types may be left out where the expected `fn` type is known
`array_map(fn($i) => ..., $items)`, `usort($xs, fn($a, $b) => ...)` and arguments to an `fn(...)` parameter
take their types from that parameter. Elsewhere (`$f = fn($x) => ...` with no declared type) the types are
written: `$f = fn(int $x): int => $x * 2;`. Both PHP forms exist: `fn($x) => expr` and
`function ($x) use ($a) { ...; return ...; }`.

### C4 — local closures borrow what they use (the default)
A closure written as an argument, or assigned to a variable, is **local**: it reads the variables it uses as
read-only loans, so nothing is copied and nothing is allocated. In exchange it may not outlive them:
- it cannot be returned, stored in a property, list or map, or passed to `go`;
- while it can still be called, the variables it reads cannot be changed or moved (the same rule as any loan,
  ownership-v2 R2): `$limit = 5; $f = fn($x) => $x < $limit; $limit = 9;` is an error naming both lines.
  Written as an argument (the common case) the loan ends with the call, so this never comes up.

An `fn` parameter is local inside the function that receives it (it may be called, not kept), like every
parameter is a loan.

### C5 — `use (&$x)`: a local closure that changes a variable
`$count = 0; array_map(function ($i) use (&$count) { $count++; return $i; }, $xs);` — an exclusive loan
(ownership-v2 R4): nothing else uses `$count` while the closure can run. Arrow functions (`fn`) never change
captures, as in PHP.

### C6 — escaping closures own what they keep
A closure that is returned, stored, or given to `go` **owns** its captures: numbers, bools and strings are
copied into it; lists, maps and objects are **moved** into it (as `$b = $a` moves them), so the variable cannot
be used after the closure is made, and `copy($xs)` keeps one for yourself. The compiler decides local or
escaping from where the closure goes; nothing is written for it. `use (&$x)` is an error in an escaping
closure (the variable would be gone when it runs). An escaping closure is a heap value with one owner like a
list: freed with its owner, moved on assignment, `copy()` copies what it captured.

### C7 — no globals, no surprises across threads
Captures are values of the function that makes the closure, never globals (Pin has none), so a closure given to
`go` is like a task argument: owned, and the same rules as `go` arguments (no `db`, `rows`, subscriptions).
A closure cannot capture itself (no recursion through captures): write a named function.

### C8 — speed
A closure literal passed straight to `array_map`, `array_filter`, `usort` (and the other built-ins that take one)
is compiled into the loop: no call through a pointer, no allocation — the same code the name forms make today.
Passed to your own `fn` parameter it is an indirect call with a pointer to the captured loans on the stack.
Only escaping closures allocate (once, when made). Programs without closures compile to the same code.

## Example error messages
```
shop.pn:12: error: this closure reads $limit (line 10), and $limit changes on line 14 while the closure can still
  be called (line 16). Change it after the last call, or let the closure have its own: $l = $limit; fn($x) => $x < $l
shop.pn:20: error: discounter() returns this closure, so it keeps $rates (moved into it on line 19): $rates can
  no longer be used here. Use copy($rates) to keep one
shop.pn:31: error: use (&$total) cannot be in a closure that is returned: $total would be gone when it runs
shop.pn:8: error: fn($x) => ... needs the type of $x here: write fn(int $x): int => ..., or pass it where an
  fn(int): int is expected
```

## Build plan (each step its own tests, compile errors and ASAN run)

1. **`fn` types, named functions as values (C1, C2)**: `fn(T): R` in the type grammar, `name(...)`, `$f($x)`
   as an indirect call; `fn` parameters. A value is a code pointer plus a null environment.
2. **Local closures (C3, C4)**: `fn($x) => ...` and `function () use (...) { }` with read-only captures; inlined
   into `array_map` / `array_filter` / `usort` / `array_reduce` (new) / `array_walk` (new); otherwise the
   environment is a stack block of pointers to the captured variables. The loan check is the existing R2
   machinery ("last use" in evaluation order, as for borrowed list items).
3. **`use (&$x)` (C5).**
4. **Escaping closures (C6, C7)**: a heap environment owning copies and moved values, a generated free /
   copy function per closure, `go` with a closure.

Steps 1–2 cover almost every closure in PHP code (callbacks written where they are used); 3–4 can wait for a
real need.

## Open questions for the owner

- **Q1** Escaping closures (C6): lists, maps and objects are **moved** into them, consistent with `$b = $a`.
  The other choice is copying them (PHP-like, but a hidden copy, against "no copies nobody asked for").
  Proposed: move, with an error message that says how to `copy()`.
- **Q2** Leaving out parameter types where the expected type is known (C3). Proposed: yes — it is what makes
  `array_map(fn($i) => $i->price, $items)` read like PHP, and the types are still checked.
- **Q3** Order: build steps 1–2 now (the callbacks people write every day) and 3–4 later. Proposed: yes.

## As built (steps 1–2, 2026-11-09)

- **Representation:** an `fn` value is `{ code, env }` in two registers. `code` is a trampoline `(ptr env, args...)`;
  for `name(...)` it is a wrapper and `env` is null. A closure's body is compiled as a function of its captures
  followed by its parameters (captures arrive as read-only loans, like every parameter), and `env` is a block in
  the enclosing function's stack frame holding the captured values. Nothing is allocated.
- **Captures:** `fn` captures every variable of the enclosing function its body names (and `$this` in a method);
  `function () use ($a)` only those listed. A scalar `use ($n)` changed inside the closure changes its own copy, as
  in PHP; lists, maps, objects and strings are loans and cannot be changed.
- **C3:** parameter types come from the expected `fn` type; the result type from the expected type, a declared
  `: T`, or (for `fn`) the body's expression. `array_map`'s result type is the closure's result.
- **C4:** a closure written as an argument lends its captures for that call only. A closure assigned to a variable
  keeps what it reads (and what those borrow from: a foreach list, `$u = $users[0]`'s list) read-only for the rest
  of the function — "last use" is not tracked yet, so this is stricter than C4 (safe, never unsafe).
- **Escapes refused (step 4):** returning an `fn`, `fn` properties, lists and maps of `fn`, `go` with an `fn`
  argument, a closure returning a closure. `json_encode`, `copy`, `==` and `echo` of an `fn` are errors.
- **Built-ins:** `array_map`, `array_filter`, `usort` (through a context adapter around the runtime's stable merge
  sort) and the new `array_reduce` take closures, fn values and names. Measured (20M ints, M2):
  `array_map(fn($x) => $x * 2 + $k, $xs)` 0.09 s, `array_map("dbl", $xs)` 0.10 s, a hand-written foreach 0.06 s
  — LLVM inlines the trampoline, so a closure costs what a named function does.
- **Unchanged code:** the IR of the 75 existing programs is the same apart from new `declare` lines.
- Tests: `tests/closures.pn`, `closures_more.pn`; errors `tests/errors/closure_*.pn` (6).
