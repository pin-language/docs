# Pin — Error handling

**Status (Pin 0.4, 2026-10-25):** `throws` / `try` / `catch` are **not built yet**. The panic side (E-R6) is
built: a panic inside an HTTP handler answers 500, frees everything the request allocated, closes its open
database handles, and the server keeps running. Agreed with the owner on 2026-10-24, replacing the earlier
default of PHP-style try/catch.

Decision rule: memory safety > speed > clarity > looking like PHP (see `ownership-v2.md`).

## Decisions

| # | question | chosen | decided by |
|---|---|---|---|
| E1 | style | **Swift/Zig style**: `throws` + `try` at the call + `catch`, compiled to return values, not stack unwinding | the owner |
| E2 | error type | one `Error{int code, string message}` for now (user-defined error classes after classes exist) | the rule: fastest, can be built at once |
| E3 | an error escaping a handler | status from `code` if 400–599, else 500 · **the body does not include the message**, only the standard status text · the message goes to the log | the rule: security first (no internal details leak to clients) |

## Rules

### E-R1 — declare `throws`
```php
function findUser(int $id): User throws {
    if ($id <= 0) { throw error(400, "bad id"); }
    throw error(404, "user $id not found");
}
```
A function not declared `throws` cannot `throw` or pass an error on (compile error).

### E-R2 — every call needs `try`
```php
$u = try findUser($id);                       // on error, pass it on (this function must be throws too)
$u = try findUser($id) catch ($e) {           // handle it here: the block must return, throw, or give a value
    http_status($e->code);
    return json_encode(["error" => $e->message]);
};
try { ... } catch ($e) { ... }                // block form for several lines
$u = findUser($id);                            // compile error: findUser() can fail, write try findUser(...)
```

### E-R3 — how it runs
- A `throws` function returns two values: the normal result and an error pointer (null = success), in
  registers.
- `try` is one branch after the call; on error it frees what the function owns (ownership rules as usual) and
  returns.
- No unwinding tables and no stack walking: it uses the ordinary return path, which ASAN already covers.
- `throw error(404, "literal")` allocates nothing (string literals have `cap = -1`); `"user $id not found"`
  allocates only when it is actually thrown.

### E-R4 — ownership and errors
- The ownership checker treats every `try` as an exit from the function: owned values are freed, moved ones are
  not freed twice. It uses the same per-path analysis (`class Flow`) as everything else.
- Something lent with `&` may be half-changed when an error happens — not a memory-safety problem, but it
  must be documented.
- `$e->message` belongs to `$e` in the catch block and may be moved out (returned).

### E-R5 — the `serve()` handler
```php
function handle(string $method, string $path, string $body): string throws { ... }
```
- An escaping error → status as in E3, body `{"error":"Not Found"}` (the standard status text), and
  `code + message + path` logged to stderr.
- The server goes on with the next request.

### E-R6 — panics are separate from errors (built)
| | error (`throws`) | panic |
|---|---|---|
| for | expected problems: bad input, not found | bugs: index out of range, division by zero, missing map key, allocation too large |
| caught by `catch` | yes | **no** |
| in a server | answered as in E3 | the request is abandoned and answered 500; the next request is served (built) |
| outside a server | escaping the top level: print and exit(1) | print and exit(1) |

Panics in a server are safe to recover from because there are no globals: one request's data never mixes with
another's. Built as: every heap block has a header and is linked to the current request; a panic longjmps
back to the worker, closes the request's database handles, and frees its blocks.

## Example error messages

```
api.pn:12: error: findUser() can fail. Write try findUser($id), or handle it with try findUser($id) catch ($e) { ... }
api.pn:20: error: throw is only allowed in a function declared with throws. Add throws after the return type
api.pn:31: error: this catch block must return, throw, or give a value of type User
```

## Implementation order

1. ~~Build on macOS~~ — done (0.1).
2. ~~Per-path analysis~~ — done (`class Flow`, 0.1).
3. `throws` / `try` / `catch` and the handler (E-R1 to E-R5) — to do.
4. ~~Panic → 500~~ — done (0.1; resources added in 0.3).
5. Measure: successful requests and 404 requests, before and after `throws`.
