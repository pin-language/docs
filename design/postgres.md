# Pin — PostgreSQL (P4)

**Status (2026-10-26):** design draft, **nothing built**. Prerequisite P4 for the web framework
([tack.md](tack.md)); builds on the connection pool ([pool.md](pool.md)). Decisions are made by the rule;
open questions for the owner are at the end. Checked on the owner's Mac: PostgreSQL 16.14 and libpq are
installed (Homebrew), so this can be built and tested locally.

Decision rule: memory safety > speed > clarity > looking like PHP.

## What it looks like

The same `db_*` functions as SQLite; the path decides:

```php
$db = db_open(env("DATABASE_URL"));            // "postgres://app@127.0.0.1/shop" — credentials never in source
$n = db_exec($db, "INSERT INTO orders (item, qty) VALUES (?, ?)", [$item, strval($qty)]);
$r = db_query($db, "SELECT id, item FROM orders WHERE qty > ?", ["1"]);
while (db_next($r)) { echo db_int($r, "id"), " ", db_string($r, "item"), "\n"; }
echo db_json($db, "SELECT id, item, qty FROM orders ORDER BY id", []);
```

## Rules

### G1 — libpq, not our own protocol
PostgreSQL's own client library (like `sqlite3` for SQLite): SCRAM authentication, TLS to managed databases
and every protocol detail are done by code the PostgreSQL project maintains. Linked only into programs that
open a `postgres://` database (like `-lsqlite3` today). Linux needs `libpq-dev`; macOS `brew install libpq`.

### G2 — a query never blocks the thread
libpq's non-blocking calls (`PQconnectStart`/`PQconnectPoll`, `PQsendQueryParams`, `PQconsumeInput`,
`PQisBusy`) with the connection's socket handed to the scheduler's `wait_fds()` (the same waiting the HTTP
client uses): while one request waits for the database, the other requests on its thread run. A cancelled
request (client gone, later a deadline) stops waiting and the connection is closed, not pooled (pool.md K4).

### G3 — `?` placeholders stay
SQL in Pin is a literal, so the compiler rewrites `?` to `$1, $2, …` outside quotes and comments at compile
time. Programs move between SQLite and PostgreSQL without touching placeholders; values always go as
parameters (`PQsendQueryParams`), never into the SQL text.

### G4 — the pool and its session rule
pool.md applies unchanged: connections per thread and per URL, returned clean (`ROLLBACK` when a transaction
is open: `PQtransactionStatus`), closed after a panic or cancellation. K4 for PostgreSQL makes these compile
errors: `SET` without `LOCAL`, `RESET`, `LISTEN`/`UNLISTEN`, `PREPARE`/`DEALLOCATE`, `CREATE TEMP`,
`DISCARD`, `SET ROLE`/`SET SESSION AUTHORIZATION`. Limits: threads × per-thread must stay under the server's
`max_connections` (default 100); the server prints the total at start.

### G5 — results
- `db_int` / `db_float` / `db_string` / `db_is_null` read the text result (`PQgetvalue`), parsed strictly:
  `db_int` on a column that is not an integer panics (as SQLite's reads are strict about the column name).
- `db_json`: numbers (`int2/4/8`, `float4/8`, `numeric`) as JSON numbers, `bool` as `true`/`false`, `json` /
  `jsonb` as they are, `NULL` as `null`, everything else as strings.
- `db_exec` returns rows changed (`PQcmdTuples`); a constraint violation (SQLSTATE class 23) returns -1 and
  `db_error()` says which, like SQLite. Other errors panic (a bug in the SQL).
- `db_last_id`: PostgreSQL has none. Use `INSERT ... RETURNING id` with `db_query`; `db_last_id` on a
  PostgreSQL connection is a compile error when the compiler can see it, else a panic with that advice.

### G6 — dynamic filters without SQL injection (also for SQLite)
Today the SQL must be one literal, so a search with optional filters needs a query per combination. New: a
string variable built **only from literals** on every path is accepted as SQL. The compiler tracks it in
`class Flow` (one more per-variable fact, like "assigned"):

```php
$sql = "SELECT id, item, qty FROM orders WHERE 1 = 1";
list<string> $ps = [];
if ($item != "") { $sql .= " AND item = ?"; $ps[] = $item; }
if ($min > 0)    { $sql .= " AND qty >= ?"; $ps[] = strval($min); }
if ($sort == "qty") { $sql .= " ORDER BY qty"; } else { $sql .= " ORDER BY id"; }
echo db_json($db, $sql, $ps);
```

- Any non-literal piece (`$sql .= $sort`) makes the variable untrusted on that path; passing it to `db_*` is
  the same compile error as today, with the advice to choose between literals with `if`.
- G3's `?` rewrite then happens at run time for these (cheap: the pieces are known to be literals).
- This keeps the guarantee — nothing a client sends can become SQL text — while allowing real search
  endpoints. (Prior art: "trusted types" for DOM sinks; Go's `database/sql` relies on discipline instead.)

### G7 — credentials from the environment
New built-in `env(string $name): string` (`""` when unset). A `postgres://` URL written as a literal in the
program is a compile error ("read it with env(\"DATABASE_URL\")"), so passwords do not end up in git.

## Tests
- Linux CI: a `postgres:16` service container; the same SQL tests as SQLite where the SQL is portable, plus
  RETURNING, constraint errors, a transaction left open (rolled back), a panic mid-query (connection closed),
  a client leaving while its query runs, two handlers waiting on the database on one thread (both progress).
- macOS CI: build only (no server), so linking is checked.
- ASAN + UBSAN on the server tests (`run_tests.py --sanitize`).

## Implementation order
1. `env()`; G6 trusted SQL variables (useful for SQLite at once).
2. libpq linking and detection (`needs_postgres`), blocking first; G3, G5.
3. G2 non-blocking with `wait_fds`; G4 pool reuse; K4 rules for PostgreSQL.
4. CI service container, sanitizers, docs (reference/database.md, AI guide).

## Open questions for the owner
- **Q1** TLS: libpq does TLS itself (needed by most managed PostgreSQL services), while design/tls.md keeps TLS
  out of Pin's HTTP and uses a proxy. Proposed: allow it for PostgreSQL, because it is libpq's code, not Pin's,
  and there is no proxy for the database protocol in common use.
- **Q2** `db_open()` of a server that is down panics (500), like SQLite's open failure. With a network database
  this is normal operation, so it could be `throws` (503). Proposed: keep panic for now, revisit with Tack.
- **Q3** G6 changes what compiles (more programs are accepted, none rejected). Proposed: yes.
