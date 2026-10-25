# Tack — the web framework for Pin

**Status (2026-10-25):** design draft, **nothing built, on hold** until the language prerequisites below are
done (owner, 2026-10-25, after a review of this draft). Name and install model agreed with the owner; the
rest was decided in the same brainstorm by the rule below and is open to change until milestone M1 is built.
Open questions for the owner are in the last section.

## Prerequisites (in the language, before Tack)

The review of this draft found that Tack would be fast only in hello-world: the language is missing parts
every web app needs, framework or not.

| # | what | why it blocks Tack |
|---|---|---|
| P1 | **resources that outlive a request** ([pool.md](pool.md)) — **built** (SQLite, 2026-10-26) | no globals means a new connection per request; fine for SQLite, far too slow for PostgreSQL |
| P2 | `json_decode` into a class — **built** (2026-10-26) | T3 validation, T8 typed client calls, class return values |
| P3 | `null` (null.md) and parameter defaults — **defaults built** (2026-10-26); null has a build plan, not built | optional query values and JSON fields (defaults cover these now) |
| P4 | PostgreSQL on the pool, plus a safe way to build queries with optional filters and sorting — **designed** ([postgres.md](postgres.md)) | the literal-SQL rule allows no search/filter endpoints today; T7's build-time check only covers SQLite |
| P5 | crypto built-ins (random tokens, sha256/HMAC, password hashing) — **built** (2026-10-26) | real auth (T4); packages cannot contain C |

Then build **M1 only** and use it for one real app before deciding which of M2–M6 to build.

Decision rule: memory safety > speed > clarity > looking like PHP.
Main users are AI coding agents: every rule below is chosen so that a mistake is a **build error with the fix
in the message**, not a bug found in production.

## Why

`serve(8080, "handle")` plus `if ($route == ...)` works, but every app re-writes the same parts and an agent
can get each of them wrong: routing and 404/405, reading path and query values, checking request bodies,
remembering auth on every route, SSE details (resume, ping, client left), timeouts across parallel calls.
Tack does these once, mostly **at build time**, so the running program is the same kind of code a person
would write by hand.

Where it lives (HANDOFF §4b): the framework is a Pin package (`github.com/pin-language/tack`, Pin source
only). The parts that must run at build time — reading `routes/` and `migrations/`, the checks — are in the
`pin` compiler, because a package cannot take part in compiling. See open question Q2.

## Compared with other frameworks (from memory, not re-checked against their current docs)

| | routes declared by | validation | auth | test client | OpenAPI | ORM |
|---|---|---|---|---|---|---|
| Laravel (PHP) | route file → controller | Form Request | middleware | built in | package | Eloquent |
| Next.js (JS) | **files** | none (zod) | one `middleware.ts` | none | none | none |
| FastAPI (Python) | decorators | **from type hints** | `Depends()` | built in | **built in** | none |
| Django (Python) | `urls.py` | forms / DRF | middleware | built in | DRF + package | built in |
| Go net/http 1.22 | `"GET /users/{id}"` strings | none | wrap handlers | `httptest` | none | none |
| Gin (Go) | `r.GET` | struct tags | middleware | `httptest` | swaggo | none |
| Axum (Rust) | builder | **from types** | tower | by hand | utoipa | none |
| **Tack** | **files** | **from types + constructor** | **folder guards, deny by default** | built in | built in | none: SQL checked at build |

Tack takes file routing from Next.js and "types are the validation and the API description" from
FastAPI/Axum. Do not claim it is the first to combine them without searching.

## Install and commands

```bash
curl -fsSL https://raw.githubusercontent.com/pin-language/tack/HEAD/install.sh | sh   # Pin + the `tack` command
tack new myapi                                                                     # project; Tack locked in pin.lock
```

Like Laravel: one install per machine (Pin, as Herd/php.new install PHP), the framework itself per project
(as `vendor/laravel/framework` + `composer.lock`), so projects on one machine can use different Tack versions.
Pin's own `install.sh` stays for programs without Tack.

| command | does |
|---|---|
| `tack new <dir>` | project skeleton: `routes/_guard.pn`, `routes/health.pn`, `migrations/001_init.sql`, `pin.lock` |
| `tack dev` | build + run, rebuild when a file changes *(later)* |
| `tack build` | one native binary, plus `build/openapi.json` |
| `tack routes` | table: method, path, file, guard, deadline |
| `tack test` | runs `tests/*.pn` with the in-process client (T9) |
| `tack migrate` | applies `migrations/*.sql` not yet applied |

`tack` is a thin wrapper over `pin`. The Tack package states the lowest Pin version it needs; an older Pin
stops with "Tack x.y needs Pin ≥ a.b: run …" (pin.lock cannot express this yet).

## Rules

### T1 — a file is a route

```
routes/
  _guard.pn               guard for everything below (T4)
  health.pn               /health
  users/index.pn          /users
  users/[id].pn           /users/{id}
  users/new.pn            /users/new           (a fixed segment beats [id])
  orders/[id]/items.pn    /orders/{id}/items
  files/[...rest].pn      /files/{rest...}      (catch-all, the rest of the path)
```

- A route file exports functions named after methods: `get post put patch delete`, and `stream` (T5).
  Other exported names are a build error; helpers stay unexported.
- Matching order per segment: fixed name, then `[param]`, then `[...rest]`. Two files that can match the same
  path with the same rank (`[id].pn` and `[slug].pn` in one folder) are a build error.
- A path that matches no file: **404**. A file without that method: **405** with an `Allow` header.
  `HEAD` is answered from `get`. `OPTIONS` is answered by Tack (CORS, T4).
- A trailing slash is not stripped: `GET /users/` answers 308 to `/users`; other methods get 404.
- The build turns the tree into one generated `handle()` (segment by segment, not a long if-chain) and calls
  `serve()` with it. The generated file is kept in `build/` for reading; `tack routes` prints the table.

### T2 — you get what the parameters ask for, and pay only for that

The generated code reads the handler's parameters and passes only those:

| parameter | comes from | when it does not fit |
|---|---|---|
| `int $id`, `string $slug` named like a `[param]` | the path | `int` that does not parse → 400 |
| `int $limit`, `string $q`, … not in the path | the query string | missing or not an `int` → 400 |
| one class that is not the guard's type, e.g. `OrderInput $in` | the JSON body (T3) | 400 naming the field |
| the guard's type, e.g. `User $me` | the guard (T4) | the guard's own error (401/403) |
| `tack::Req $req` | the raw request: method, path, headers, query, body text | — |

- A `[param]` with no parameter of that name is fine (not read); a parameter that fits no row is a build error.
- Optional query values need parameter defaults, which Pin does not have yet; until then read them from
  `tack::Req` (`$req->query_has("limit")`).
- Return `string` (sent as it is), or a class / list / map (sent through `json_encode`; also gives the
  OpenAPI response type). Status: `http_status()`, or `throw error(code, msg)` from a `throws` handler.

```php
// routes/users/[id].pn
export function get(int $id, User $me): UserView throws {
    $db = db_open("app.db");
    return try users::view($db, $id);
}
```

### T3 — validation: decode into a class, rules in its constructor

```php
class OrderInput {
    public function __construct(public string $item, public int $qty) throws {
        if ($qty < 1 || $qty > 100) { throw error(400, "qty must be 1-100"); }
        if (strlen($item) == 0 || strlen($item) > 200) { throw error(400, "item must be 1-200 bytes"); }
    }
}
// routes/orders/index.pn
export function post(User $me, OrderInput $in): string throws { ... }
```

- Layer 1, generated: JSON → class. A missing field, a wrong type or an **unknown field** answers 400 with
  `{"error":"...","field":"qty"}`. Fields map to constructor parameters by name and the object is made with
  `try new`; a class without a constructor gets its properties filled.
- Layer 2, written by hand: business rules in `__construct ... throws` (already in Pin). Holding an
  `OrderInput` means it passed: there is no "forgot to validate" path.
- The first error is reported (a list of all field errors: later). Body size and UTF-8 limits stay in the
  server (0.6.0 limits; strings.md for UTF-8).
- The same decoder reads JSON from other servers: `$u = try tack::get_json($url, [], 2000)` into a typed
  variable `UserDto $u` (T8).

### T4 — guards per folder, deny by default

```php
// routes/_guard.pn — every route below needs a signed-in user
export function guard(tack::Req $r): User throws { return try auth::user($r); }

// routes/public/_guard.pn — public on purpose
export function guard(tack::Req $r): tack::Anon { return new tack::Anon(); }
```

- Every route is under at least one `_guard.pn`; **the root one is required** (missing = build error). A
  public route is one whose guard says so in code.
- The nearest `_guard.pn` up the tree runs, only that one. To build on another guard, call it: guards are
  one line that calls ordinary functions in a normal module (`auth::user`, `auth::admin`). No hidden chain.
- A handler asking for a type its guard does not return is a build error; not asking is fine (the guard
  still runs). `tack routes` shows the guard of each route.
- Cross-cutting settings are data, not code: CORS origins, request body limit, log format in `tack.json`.
- Auth helpers in the package: API keys (works today) and **session tokens kept in SQLite** (revocable;
  preferred over JWT: no algorithm choice to get wrong). A signed token checked without the database (HMAC)
  is an option for routes where the per-request SQLite lookup is too slow. Both need new built-ins (below).

### T5 — realtime: `stream` routes

```php
// routes/rooms/[room].pn
export function post(string $room, User $me, ChatInput $in): string throws {
    tack::emit("room:$room", json_encode($in));
    return "{\"ok\":true}";
}
export function stream(string $room, User $me): string {
    return "room:$room";                          // the Hub topic to follow
}
```

- `stream` answers `GET` when the request has `Accept: text/event-stream` (otherwise `get`, or 406).
- Tack does the rest: `sse_start`, `hub_resume` from `Last-Event-ID`, `sse_send_id` with `hub_last_id`, a
  ping comment when nothing came for 25 s, return when the client leaves (499). The guard runs first.
- `tack::emit($topic, $text)` is `hub_publish`. `tack::emit_saved($db, $topic, $text)` *(later)* also writes
  the event to SQLite, and a resume older than the Hub's 100 kept messages reads from there.

### T6 — a deadline for the whole request

```php
// routes/dashboard.pn
export function deadline(): int { return 300; }   // ms; may also be in a folder's _guard.pn
export function get(User $me): string throws {
    $a = go api::orders($me->id);
    $b = go api::stock();
    $o = try await $a;
    $s = try await $b catch ($e) { "[]"; };        // slow or failed: carry on without it
    ...
}
```

- When the time is up the request is cancelled the same way as when the client leaves (the server already
  sets `cancelled` and wakes the request's tasks): every wait (`await`, `sleep_ms`, `hub_next`, `http_*`,
  `run`) fails, pending tasks are cancelled, the answer is 504.
- No context parameter to pass around (Go's `ctx`): tasks are structured, so they all belong to the request.
- Limit: cancelling happens only at waits (concurrency.md C6); a long computing loop runs until its next wait.

### T7 — no ORM; SQL checked at build time

```
migrations/001_users.sql
migrations/002_orders.sql
```
```php
list<User> $us = try db_all($db, "SELECT id, name FROM users WHERE team = ?", [$team]);
User $u = try db_one($db, "SELECT id, name FROM users WHERE id = ?", [strval($id)]);   // none → 404
```

- An ORM is not a fit: lazy relations hide queries (N+1) and do not sit well with ownership (objects move),
  and Pin's literal-SQL rule (no injection) already makes SQL the safe path. Agents write SQL well.
- At build time the compiler applies every migration to an in-memory SQLite (Python's `sqlite3`, no extra
  package) and prepares every SQL literal: an unknown table or column, a wrong number of `?`, or selected
  columns that do not match the target class's properties are build errors.
- Prior art: sqlx (Rust) checks queries against a database at compile time; sqlc (Go) generates code from SQL.
- PostgreSQL (HANDOFF §4 item 7) is harder: checking needs a running server or a SQL parser. Decide then.

### T8 — the API describes itself: OpenAPI and MCP

- From T1–T3 the build knows every route, its parameters, body class and return type. `tack build` writes
  `build/openapi.json`; the app serves it at `/_tack/openapi.json` (behind the root guard).
- **MCP** *(opt-in, `"mcp": true` in tack.json)*: the same data becomes MCP tools served over HTTP at
  `/_tack/mcp`, e.g. `POST /orders` → tool `create_order {item: string, qty: int}`. An API written with Tack
  is a tool for AI agents without extra code. Guards apply. Builds on the stdio package `pin-language/mcp`.
- Typed client calls: `tack::get_json` / `tack::post_json` decode answers with the T3 decoder.

### T9 — testing without a port

```php
// tests/orders.pn
$r = try tack::test("POST", "/orders", ["Authorization" => "Bearer t1"], "{\"item\":\"cake\",\"qty\":2}");
if ($r->status != 201) { throw error(1, "POST /orders: want 201, got " . $r->status . ": " . $r->body); }
```

- `tack::test` calls the generated `handle()` in the same process with a made-up request: no server, no
  port, so agents can run it inside their `pin check` loop.
- Needs runtime support for a request that did not come from a socket (headers, status, response headers).

### T10 — workers and jobs *(later)*

Pin has no fire-and-forget tasks (structured on purpose), so no "dispatch a job and return". Instead: the
job goes into a SQLite table plus `tack::emit("jobs", $id)`; a worker is a separate Pin program that follows
`/_tack/jobs` with `http_stream` and reconnects with `stream_last_id`, running jobs in parallel with `go`.

## Speed

The rule: if a feature makes the scores drop, cut it first.

- Zero run-time cost: reading `routes/`, guard coverage, SQL checks, OpenAPI/MCP schemas — all at build time.
  (Laravel without Octane boots the framework on every request; Tack has nothing to boot.)
- Small: segment matching, parsing path values, one timer per request for routes with a deadline.
- Decoding a body once may be faster than today's `json_string($body, "k")` per field. Not measured.
- The real costs are the app's choices (a SQLite session lookup per request, `emit_saved` writes).
- **Gate in Tack's CI:** `GET /hello` and `GET /users/{id}` through Tack vs the same code with plain `serve()`:
  at most 5% slower, or no release. Nothing is measured yet; 5% is a starting value.

## What Pin needs

| need | for | kind |
|---|---|---|
| `json_decode` into a class (generated decoder per class, like the `json:` encoders) | T3, T8 | compiler |
| read `routes/`, generate `handle()`, check guards and parameters | T1, T2, T4 | compiler / `pin` CLI |
| apply migrations and prepare SQL literals at build time; `db_all` / `db_one` into classes | T7 | compiler |
| request deadline that cancels like a client leaving | T6 | runtime |
| a request not from a socket | T9 | runtime |
| `random_token()`, `sha256()`, `hmac_sha256()`, `password_hash()` / `password_verify()` | T4 | built-ins (C) |
| "needs Pin ≥ x" in a package | install | `pin get` / pin.lock |
| `tack` command and `install.sh` | install | tack repo |

## Error messages (examples of the style)

```
routes/users/[id].pn:3: parameter $uid matches nothing: the path has {id}, the guard gives User. Rename it to $id?
routes/admin/stats.pn: no _guard.pn covers this route. Add routes/_guard.pn (every route needs one;
  for a public route write a guard that returns tack::Anon)
routes/orders/index.pn:7: SQL: no column "qyt" in table orders (columns: id, item, qty)
routes/a/[id].pn and routes/a/[slug].pn match the same paths: keep one
```

## Implementation order

1. **M1** — package core (`tack::Req`, errors), file routing + 404/405/308, path and query parameters,
   `tack routes`, `tack::test`, the speed gate. Enough for real apps with hand-written checks.
2. **M2** — `json_decode` into classes → body parameters, validation, class return values, OpenAPI.
3. **M3** — guards with deny-by-default; crypto built-ins; API keys and sessions.
4. **M4** — `stream` routes, request deadline.
5. **M5** — migrations and build-time SQL checks, `db_all` / `db_one`.
6. **M6** — MCP, `emit_saved`, workers, `tack dev`.

After each: tests for every feature and every new build error, ASAN/UBSAN for runtime parts, a fresh-agent
test with only the AI guide (HANDOFF §1), and the speed gate.

## Open questions for the owner

- **Q1** Deny by default (T4): every route must be under a guard, public routes say so. Strict but it closes
  the most common hole. Proposed: yes.
- **Q2** The compiler knows about `routes/` and `migrations/` (HANDOFF §4b says frameworks stay out of the
  language). Proposed: the compiler only checks and generates; Tack's code stays in the package.
- **Q3** Crypto built-ins in the language (needed for real auth; packages cannot contain C). Proposed: yes,
  a small set, from a reviewed C implementation.
- **Q4** MCP off by default (opt-in). Proposed: yes — exposing every route to agents should be a choice.
