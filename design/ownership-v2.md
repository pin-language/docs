# Pin — Ownership v2: `list<string>`, nested containers, classes

**Status (Pin 0.5, 2026-10-25):** **built**, R1–R7 and nested containers, with these differences:
- R2 borrows lists, maps and objects; strings read from a container are still copied (D4 not built).
- "Last use" is approximated in evaluation order (plus loop rounds), so a few safe programs are rejected —
  never an unsafe one. The message names the line of the later use.
- R4 `&` works on variables and paths; not on bool items inside containers. `&$this` is not allowed (it
  would let a callee replace the object a method is running on); `&$this->prop` is.
- The call's other arguments may not use a value lent with `&`, nor the receiver of a changing method.
- A class cannot hold itself directly (no null yet): use `list<Node>` or an id.

## Decision rule (chosen by the owner)

In order of priority:

1. **Memory safety** — no use-after-free, double free, or out-of-bounds reads and writes. Confirmed by the
   owner: it comes before speed. Bounds checks are always on: no `unsafe`, no flag to turn them off. Speed comes
   from the compiler / LLVM proving checks redundant and removing them.
2. **Speed at run time** — no hidden costs: no garbage collector, no reference counting, no copies nobody
   asked for.
3. **Clarity** — reading the code shows where data changes and where it is copied.
4. **Looking like PHP — the lowest priority.** Use PHP syntax when it does not conflict with 1–3.

## Decisions

| # | question | chosen | why |
|---|---|---|---|
| D1 | is an object a value or a handle? | **a value** with one owner; assignment moves it, like a list | no reference counting at run time |
| D2 | `$u = $users[0];` | **a read-only borrow**: no copy, no error | fastest (an earlier proposal made it an error; borrowing is faster and easier to use) |
| D3 | `&` at the call site | **written at both the declaration and the call**: `discount(&$o)` | no speed difference, so the clearer form (rule 3) wins over PHP's (rule 4) |
| D4 | strings read from a list or map | the same as D2: borrowed, not copied | no hidden copies |

## Rules

### R1 — every heap value has exactly one owner
Lists, maps, strings and objects as today; memory is freed when the owner goes away.
```php
$b = $a;          // list / map / object: moves; $a can no longer be used
$t = $s;          // string: still a copy (unchanged)
```

### R2 — reading through an index borrows, within one function (new)
```php
$u = $users[0];            // $u borrows $users[0] read-only, no copy
echo $u->name;             // fine
$u->name = "x";            // error: $u is borrowed and cannot be changed
$users[] = $new;           // error: $users is borrowed by $u (still used on line 7)
echo $u->name;
```
- A borrow lives **only inside one function** and ends at the last use of `$u` (like Rust's non-lexical
  lifetimes, but never across functions).
- A borrowed variable cannot be stored in a list, map or field, nor returned, so the compiler needs no
  lifetime annotations.
- To get your own value: `copy($users[0])`. To move it out: `array_pop()`, `array_shift()`, `take($users, $i)`.

### R3 — change through a path directly
```php
$users[0]->name = "x";
$m["a"]["b"] += 1;         // a map of maps
$order->items[] = "tea";   // a list<string> inside an object
```

### R4 — `&` is a borrow that may change, written on both sides
```php
function discount(Order &$o): void { $o->total -= 10; }

discount(&$order);         // fine
discount($order);          // error: write &$order
discount(&$orders[0]);     // fine
swap(&$a[0], &$a[1]);      // error: $a borrowed for changing twice at once
```
- While borrowed with `&`, the original cannot be used any other way (exclusive).
- A parameter without `&` stays a read-only borrow, as today.

### R5 — foreach
```php
foreach ($users as $u)  { echo $u->name; }    // read-only borrow
foreach ($users as &$u) { $u->age += 1; }     // a borrow that may change (no copy)
```
Adding to or removing from the container while looping stays forbidden.

### R6 — methods
- A method that assigns `$this->...` or passes `$this` on with `&` is a **changing method**; the compiler
  infers it, no keyword needed.
- Calling a changing method needs the right to change the receiver: an owned variable, a `&` parameter, or a
  path into one.
```php
function show(Order $o): void { $o->recalc(); }   // error: recalc() changes $o, but $o is a read-only borrow
```

### R7 — no references pointing around
An object cannot point at its parent; use an id or index (`int $parentId`). If real code ever needs shared
objects, consider a reference-counted `shared class` later — **not planned now**.

## Example error messages

```
users.pn:7: error: cannot append to $users while $u is borrowing $users[0] (used again on line 8).
  Use $u for the last time before appending, or use copy($users[0]) to keep your own value
users.pn:4: error: $u is borrowed from $users[0] and cannot be changed.
  Change $users[0]->name directly, or use copy($users[0])
orders.pn:12: error: discount() can change its argument, so write discount(&$order)
orders.pn:15: error: $a is borrowed for changing twice in the same call (&$a[0], &$a[1])
orders.pn:20: error: recalc() changes $o, but $o is a read-only parameter.
  Declare it as Order &$o, or work on copy($o)
```

## Implementation cost (estimated, not measured)

- R2 needs per-function liveness (the line where each variable is used for the last time) — the largest new
  piece. It builds on the per-path `Flow` state that 0.1 added (`class Flow` in pinac.py).
- R4 and R6 can be checked within one function, because no reference is ever stored.

## Decided

- Concurrency: structured `go` + `await` — see `concurrency.md` (owner, 2026-10-24; not built).
- Int overflow: see `int-overflow.md` — memory-safety checks done; overflow panics on `+ - *` were built and
  then removed for speed on the owner's request.
- Name: **Pin**, extension `.pn` (owner, 2026-10-24).
- Error handling: Swift/Zig style `throws` + `try` + `catch`, compiled to return values — see
  `error-handling.md` (owner, 2026-10-24; not built).
- Memory safety comes before speed; bounds checks always on (owner, 2026-10-24).
