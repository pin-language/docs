# Pin — Concurrency

**Status (Pin 0.4, 2026-10-25):** **not built yet.** Today the only parallelism is the HTTP server, which runs
one handler per CPU core with no shared state. Agreed with the owner on 2026-10-24, replacing the earlier
decision 3A (Go-style goroutines) with **structured `go` + `await`**. Prerequisites already built: the macOS
event loop (kqueue), per-path analysis (`class Flow`), panic → 500 with per-request cleanup. Still needed
first: `throws` / `try` (`error-handling.md`).

Decision rule: memory safety > speed > clarity > looking like PHP.

## Why 3A changed

A fire-and-forget `go` (as in Go) loses errors and panics silently, leaks tasks that never finish, and lets a
task outlive its request — so it cannot borrow the request's data and must copy everything (slow). Structured
tasks fix all three and let tasks borrow data across threads without copying.

## Rules

### C1 — `go` returns a `Task<T>` that must be awaited before the function ends, on every path
```php
$u = go findUser($id);          // a Task<?User>, already running
$user = try await $u;           // f() throws → try await
$n = await go count2($xs);      // f() does not throw → plain await
```
- `Task<T>` is a value with one owner; it can move (into a `list<Task<T>>`) but not be copied.
- `await` consumes the task (a move), so awaiting twice is a compile error.
- A task not awaited when the function returns normally is a compile error.
- Leaving through `throw`, an error passed on by `try`, or a panic **cancels the pending tasks and waits for
  them to stop** before leaving.
- A task cannot be returned or stored in a property (it is awaited where it was started), so no lifetimes are
  needed.

### C2 — tasks borrow read-only data across threads without copying
- An argument without `&` is a read-only borrow that ends at `await` (not at the end of the line).
- Several tasks may borrow the same value at once.
- Meanwhile the owner cannot change or move it (rule R2 in `ownership-v2.md`).
- Safe across threads because Pin has no reference counting and no interior mutability.

### C3 — `&` lends to one task for changing, exclusively
- No other task, and not the owner, may use it until the task is awaited (rule R4).
- So **data races cannot compile.**

### C4 — errors and panics
- A task's error comes back through `await` (`try await` / `try await ... catch`).
- A panic in a task panics the whole request (500), as in `error-handling.md` E-R6.

### C5 — built-in functions
| function | does |
|---|---|
| `await_all(list<Task<T>> $ts): list<T>` | waits for all, results in the original order · `throws` if any task throws · the first error cancels the rest |
| `await_timeout(Task<T> $t, int $ms): T throws` | past the time limit: cancels the task and throws `error(504, "timeout")` |
| `await_any(list<Task<T>> $ts): T` | the first to finish; cancels the rest *(later)* |

No `timeout` keyword — a function keeps the syntax small.

### C6 — cancellation
- Cooperative: a task stops at its next I/O wait or `await`.
- Long computing loops: the compiler adds a cancellation check at the loop head *(to measure — expected to be
  tiny: one load and a well-predicted branch)*.
- After cancellation, what the task owned is freed by the ownership rules.

### C7 — runtime
- M:N green threads, work stealing between cores, one event loop shared with the HTTP server (kqueue on macOS,
  epoll on Linux).
- Each task's stack is reserved in virtual memory with a **guard page**: a stack overflow panics instead of
  overwriting memory.
- A task waiting for I/O does not block an OS thread.
- `PN_THREADS` still sets the number of OS threads.

### C8 — no async/await split like JavaScript or Rust
There are no separate "async" functions: every function can use `go`, and every function can be started with
`go`.

## Examples

```php
// several calls at once inside a handler
function profile(int $id): string throws {
    $u = go findUser($id);
    $o = go findOrders($id);
    $p = go getPoints($id);
    $user   = try await $u;
    $orders = try await $o;
    $points = try await $p catch ($e) { 0; };
    return json_encode(["user" => $user, "orders" => $orders, "points" => $points]);
}

// many tasks in a loop
function prices(list<int> $ids): list<float> throws {
    list<Task<float>> $tasks = [];
    foreach ($ids as $id) { $tasks[] = go fetchPrice($id); }
    return try await_all($tasks);
}

// several cores borrowing the same data
function stats(list<int> $xs): string {
    $half = intdiv(count($xs), 2);
    $a = go sumRange($xs, 0, $half);
    $b = go sumRange($xs, $half, count($xs));
    return json_encode(["sum" => await $a + await $b]);
}

// timeout
$points = try await_timeout(go getPoints($id), 200) catch ($e) { 0; };
```

## Example error messages
```
profile.pn:3: error: task $u started on line 2 is not awaited when the function returns on line 3.
  Add await $u before returning
stats.pn:3: error: cannot append to $xs while task $t (line 2) is reading it. Move this line after await $t
order.pn:3: error: $o is already being changed by task $a (line 2). Await $a first, or give each task its own copy()
user.pn:4: error: $t was already awaited on line 3
user.pn:5: error: findUser() can fail, so write try await $t
```

## Later

| topic | direction |
|---|---|
| channels | sending moves the value, as everywhere else · build when there is a real producer/consumer need |
| data shared across requests (cache, rate limits, connection pools) | still no user globals · the runtime provides safe ready-made types (`Cache`, `DbPool`) · decide together with PostgreSQL |
| work after the response (sending email) | not a fire-and-forget `go` · the runtime provides a queue with retries that never loses errors |

## Implementation order

Needs first: `throws` / `try`.
1. Runtime: green threads, stacks with guard pages, a scheduler per core.
2. Tie the server's I/O into the scheduler.
3. Compiler: `go` / `await` / `Task<T>` and C1–C3.
4. `await_all`, `await_timeout`, cancellation.
5. Tests: races that must not compile, cancellation on error, ASAN + TSAN clean, the cost of `go` per task.
