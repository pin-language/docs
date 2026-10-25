# Pin — Database connections that outlive a request (pool)

**Status (2026-10-25):** design draft, **nothing built**. Prerequisite P1 for the web framework
([tack.md](tack.md)) and for PostgreSQL (HANDOFF §4 item 7). Decisions below are made by the rule; the open
questions at the end are for the owner.

Decision rule: memory safety > speed > clarity > looking like PHP.

## Why

Pin has no global variables, so nothing survives from one request to the next: every handler that touches
the database calls `db_open()` and the connection is closed when the handler returns. Today (verified in
`runtime/sqlite.c`) that means per request: open the file, set `busy_timeout`, run
`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON`, prepare every statement again, close.

- **SQLite:** cheap-ish (a file open and two pragmas) but not free, and every statement is prepared again.
  Not measured yet — step 0 below measures it.
- **PostgreSQL:** a TCP connection, a startup message, authentication (SCRAM is several round-trips) and a
  server process fork per connection: milliseconds per request, which would erase Pin's speed on any app
  that uses the database. This is the real reason for P1.

PHP has the same problem (no shared state between requests) and answers it with persistent connections
(`pg_pconnect`, `PDO::ATTR_PERSISTENT`): kept by the runtime per worker process, invisible to the script.
Pin can do the same, more safely.

## What it looks like

Nothing changes in programs that work today:

```php
function handle(string $method, string $path, string $body): string {
    $db = db_open("shop.db");                  // now: takes a ready connection from this thread's pool
    ...
}                                              // $db goes out of scope: back to the pool, not closed
```

Optional settings, as top-level statements before `serve()` (configuration for the runtime, not a variable
handlers can see):

```php
db_pool("shop.db", 4, 60000);                  // at most 4 open per worker thread; close after 60 s idle
serve(8080, "handle");
```

## Rules

### K1 — the pool belongs to the runtime, one per worker thread

- Each server worker thread keeps its own idle connections, keyed by the `db_open()` argument (the path,
  later the PostgreSQL URL). Tasks never leave the thread that started them (concurrency.md), so a
  connection never crosses threads and **the pool needs no locks**.
- Programs outside `serve()` (CLI) get the same behaviour on the main thread; it only matters for programs
  that open the same database many times.
- Handlers still share nothing: the pool holds connections that nobody owns, never values from a program.

### K2 — a connection has one owner, as today

- `db_open()` gives an owned `db`. When the owner frees it (function returns, variable overwritten,
  `db_close()`), the connection goes back to the pool **only if it is clean** (K4); otherwise it is closed.
- `rows` still cannot outlive the statement's connection: a `rows` is closed before its `db` goes back.

### K3 — a connection is used by one task at a time

- Today two tasks may borrow the same `db` (`go f($db); go g($db);` compiles — checked 2026-10-25). Safe for
  SQLite because its calls never yield. For PostgreSQL a query waits on the network, so two tasks would mix
  their messages on one connection.
- New rule (compile error): a `db` or `rows` cannot be passed to `go`. Message: "a task opens its own
  connection: `$db = db_open(...)` inside the task (it comes from the pool, it is cheap)". This also stops one
  task's `BEGIN` from swallowing another task's statements.
- This breaks code that passes `db` to `go` today. No test, example or bench in the pin repo does (searched
  2026-10-25), and SQLite calls do not run in parallel anyway, so nothing is lost.

### K4 — what comes back must be clean; when in doubt, close it

A connection goes back to the pool only after a normal release. On return the runtime:
1. finalizes statements still open (they are already closed by ownership; this is a guard);
2. if a transaction is still open (SQLite `sqlite3_get_autocommit() == 0`, PostgreSQL status not idle) runs
   `ROLLBACK` — so one request's half-done transaction never leaks into the next request;
3. otherwise keeps it.

Closed instead of returned:
- after a **panic** or **cancellation** (client left, deadline) during the request — the connection may be in
  the middle of a query; closing is always safe and these are rare;
- after any I/O or protocol error on it;
- when the thread already holds its maximum of idle connections.

**Session state:** a statement that changes the connection for later users (PostgreSQL `SET` without
`LOCAL`, `SET SESSION`, `LISTEN`, `PREPARE`, `CREATE TEMP TABLE`; SQLite `PRAGMA` that writes, `ATTACH`,
`CREATE TEMP`) is a **compile error** — the literal-SQL rule means the compiler sees every statement.
Message: "this changes the connection for the next request; use `SET LOCAL` inside a transaction". This keeps
the pool safe without PostgreSQL's `DISCARD ALL` on every return (an extra round-trip, and it throws away the
prepared-statement cache of K6).

### K5 — limits and waiting

- `db_pool($key, $per_thread, $idle_ms)`; defaults: 4 per thread, 60 s idle. At start the server prints
  `pool shop.db: 8 threads × 4 = at most 32 connections` (PostgreSQL's default `max_connections` is 100).
- `db_open()` when the thread already has its maximum in use: the task **waits** (yields to other tasks on
  the thread) until one is released, at most 5 s, then fails with 503 inside a handler (panic outside).
  Waiting yields, so other requests on the thread keep running.
- Idle connections older than `$idle_ms` are closed by the worker's once-a-second scan (the same timer that
  handles connection timeouts since 0.6.0).
- A PostgreSQL connection closed by the server while idle is noticed without a round-trip (its socket turns
  readable) and dropped at checkout.

### K6 — prepared statements stay on the connection (speed)

- SQL in Pin is always a string literal, and literals are constants with a fixed address, so the address is
  a perfect cache key: each pooled connection keeps the statements it prepared (SQLite `sqlite3_stmt`,
  PostgreSQL named statements), reset and rebound instead of prepared again.
- Bounded per connection (e.g. 64, oldest out). Finalized when the connection closes.

### K7 — memory and panics

- Pool entries and the cache use plain `malloc` (like the server's `Conn`): they outlive requests, so they
  must not be request blocks. Nothing from a request's blocks is ever stored in them.
- The request's resource list (`pn_res_add`) still tracks a borrowed connection; the close function becomes
  "release": return if clean (K4), close if the request panicked or was cancelled.
- ASAN/UBSAN tests: many requests opening, panicking with an open transaction, cancelling mid-query; the
  pool's own state must be leak-free at exit (LeakSanitizer on Linux).

## Also needed for PostgreSQL (not part of P1)

- An `env("DATABASE_URL")` built-in: credentials must not be string literals in source. Pin has no `env()`
  today (checked: `pinac.py` has no such built-in).
- Non-blocking PostgreSQL protocol on the scheduler's `wait_fds`, so a query yields instead of blocking the
  thread. P4.

## Step 0 — measure first

Before building: one handler that does `db_open` + one `SELECT` per request, under load, against the same
handler with the connection kept (a hand-made test build). If SQLite gains little, K1–K5 still go in (they
are what PostgreSQL needs) but the speed claim for SQLite is dropped.

### Step 0 results (2026-10-25, owner's Apple M2, macOS, best of 3 — measured, with caveats)

CLI loop, 100,000 × (`db_open` + one `SELECT` by primary key + close), 1,000-row table:

| | time | per call |
|---|---|---|
| open + close every call (each close is the last connection: SQLite checkpoints the WAL) | 20.6 s | ~206 µs |
| open + close every call, another connection kept open | 7.7 s | ~77 µs |
| one connection for all calls | 0.35 s | ~3.5 µs |
| test-only pooled runtime (4 idle handles per thread), same code as the first row | 0.35 s | ~3.5 µs |

HTTP, handler = `db_open` + `db_json` of one row; keep-alive load generator (C, 2 threads × 16 connections,
5 s) on the same machine; 8 server threads:

| server | req/s (3 runs) |
|---|---|
| no database (same handler shape) | 275k–289k |
| today: `db_open` per request | 24.6k–26.0k |
| test-only pool | 167k–186k |

**SQLite gains ~6.8× per request**: the pool is worth it for SQLite too, not only for PostgreSQL. Caveats:
load generator on the same 8 cores; one read-only query on a tiny table (real handlers do more per request,
so the gain in real apps is smaller); macOS only, not re-run on Linux. Outputs were checked (same JSON from
both servers, 0 bad responses).

**Found while measuring:** every HTTP request wrote into freed memory (`request_done` freed the request while
`cur_req` still pointed at it; `leave_task` copied it back into the task and `task_release` wrote through it).
Under load with database handlers it crashed the server (SIGSEGV). Fixed in the pin repo; CI now runs the
HTTP servers under ASAN + UBSAN (`run_tests.py --sanitize`), which `tools/sanitize.sh` could not do.

## Implementation order

1. Step 0 measurement (SQLite).
2. K3 compile error, K2/K4 return-or-close, K1 per-thread pool for SQLite, K5 limits and waiting.
3. K6 statement cache; measure again.
4. Tests (normal, panic in transaction, cancel, pool full) + ASAN/UBSAN; ai-guide and reference pages.
5. PostgreSQL (P4) uses the same pool.

## Decisions (owner, 2026-10-25: Q1–Q3 as proposed)

- K3: a `db` / `rows` cannot be passed to `go` — **agreed**.
- K4: statements that change session state are compile errors — **agreed**.
- K5 defaults 4 per thread, 60 s idle, 5 s wait then 503 — **agreed**, to revisit after measuring.

## Questions as asked

- **Q1** K3 breaks programs that pass a `db` to `go` today. Proposed: yes (needed for PostgreSQL; no speed
  lost with SQLite).
- **Q2** Statements that change session state become compile errors (K4). Strict, but the alternative is
  either a leak between requests or an extra round-trip on every request. Proposed: yes.
- **Q3** Defaults: 4 per thread, 60 s idle, 5 s wait then 503. Proposed: yes, change after measuring.
