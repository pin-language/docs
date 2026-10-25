# Database (SQLite)

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`db_open`](#db_open) | Open (or create) an SQLite database file. |
| [`db_pool`](#db_pool) | Set the connection pool for one database file (optional). |
| [`db_exec`](#db_exec) | Run INSERT, UPDATE, DELETE or CREATE; returns the rows changed. |
| [`db_query`](#db_query) | Run a SELECT and get the rows one at a time. |
| [`db_next`](#db_next) | Move to the next row; false when there are no more. |
| [`db_int`](#db_int) | An integer column of the current row (NULL gives 0). |
| [`db_float`](#db_float) | A numeric column of the current row (NULL gives 0.0). |
| [`db_string`](#db_string) | A column of the current row as text (NULL gives `""`). |
| [`db_is_null`](#db_is_null) | Whether a column of the current row is NULL. |
| [`db_json`](#db_json) | Run a SELECT and get all rows as a JSON array of objects. |
| [`db_last_id`](#db_last_id) | The id of the last row inserted on this connection. |
| [`db_error`](#db_error) | Why the last `db_exec` returned -1, or `""`. |

## db_open

```php
db_open(string $path): db
```

Open (or create) an SQLite database file.

```php
$db = db_open(":memory:");          // a file name like "shop.db", or ":memory:" for a temporary one
echo db_exec($db, "CREATE TABLE t (x INTEGER)", []), "\n";
```

Output:

```
0
```

- When `$db` goes out of scope (end of the function) the connection goes back to a pool the runtime keeps per server thread, so the next `db_open()` of the same file is almost free (~3 µs instead of ~80–200 µs). A connection comes back only clean: an open transaction is rolled back; after a handler panics it is closed.
- Open one per request in a server — that is the intended use. WAL mode lets requests read and write in parallel; writers wait up to 5 seconds for each other.
- `:memory:` and `""` are never pooled: each open is a new, empty database.
- A file that cannot be opened panics. Foreign keys are enforced.
- `db` values move like lists; pass `$db` to functions (they borrow it). A task (`go`) cannot use the caller's `$db`: open one inside the task.
- SQL that would change the connection for its next user (`PRAGMA foreign_keys = ...`, `ATTACH`, `CREATE TEMP ...`) does not compile.
- **PHP:** Pin's version of `new PDO('sqlite:shop.db')`. PostgreSQL is planned with the same functions.

## db_pool

```php
db_pool(string $path, int $per_thread, int $idle_ms): void
```

Set the connection pool for one database file (optional).

```php
db_pool("shop.db", 8, 30000);    // up to 8 connections per server thread; close after 30 s unused
echo "pool set\n";
```

Output:

```
pool set
```

- Without it each file gets 4 connections per thread, closed after 60 s unused.
- Only at the top level of the program, before `serve()` (compile error inside a function).
- When a thread's connections are all in use, `db_open()` waits (other requests keep running) for up to 5 seconds, then panics — a 500 inside a handler. A handler holds a connection while it waits (`sleep_ms`, `await`, `http_get`), so raise the limit for handlers like that.
- **PHP:** Like `PDO::ATTR_PERSISTENT` / `pg_pconnect`, but the connection is always returned clean.

## db_exec

```php
db_exec(db $db, string $sql, list $params): int
```

Run INSERT, UPDATE, DELETE or CREATE; returns the rows changed.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
echo db_exec($db, "INSERT INTO items (name, qty) VALUES (?, ?)", ["tea", "2"]), " ";
echo db_exec($db, "INSERT INTO items (name, qty) VALUES (?, ?)", ["tea", "5"]), " ", db_error($db), "\n";
```

Output:

```
1 -1 UNIQUE constraint failed: items.name
```

- The SQL must be a string literal in your code; every value goes in a `?` placeholder and in the list (`list<string>`, `list<int>` or `list<float>`). SQL built from variables does not compile, so a client cannot inject SQL.
- Returns -1 when a constraint (UNIQUE, NOT NULL, CHECK, FOREIGN KEY) refuses the change — `db_error($db)` says which. Any other error (bad SQL, wrong number of values) is a bug and panics.
- One statement per call. Numbers can be passed as strings: SQLite stores `"2"` in an INTEGER column as 2.

## db_query

```php
db_query(db $db, string $sql, list $params): rows
```

Run a SELECT and get the rows one at a time.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name, qty, price) VALUES (?, ?, ?)", ["tea", "2", "40"]);
db_exec($db, "INSERT INTO items (name, qty, price) VALUES (?, ?, ?)", ["cake", "1", "89.5"]);
$rows = db_query($db, "SELECT name, qty, price FROM items WHERE qty >= ? ORDER BY name", ["1"]);
while (db_next($rows)) {
    echo db_string($rows, "name"), " x", db_int($rows, "qty"), " at ", db_float($rows, "price"), "\n";
}
```

Output:

```
cake x1 at 89.5
tea x2 at 40
```

- Same SQL rules as `db_exec`. Read columns by name with `db_int`, `db_float`, `db_string`, `db_is_null` after `db_next` returns true.
- `rows` close by themselves when they go out of scope; they may outlive the `$db` they came from.
- **PHP:** Like `$pdo->prepare($sql)->execute($params)` followed by a `fetch()` loop.

## db_next

```php
db_next(rows $rows): bool
```

Move to the next row; false when there are no more.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
$rows = db_query($db, "SELECT name FROM items", []);
echo db_next($rows) ? "a row" : "no rows", "\n";
```

Output:

```
no rows
```

## db_int

```php
db_int(rows $rows, string $column): int
```

An integer column of the current row (NULL gives 0).

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name, qty) VALUES (?, ?)", ["tea", "3"]);
$rows = db_query($db, "SELECT qty, qty * 10 AS big FROM items", []);
while (db_next($rows)) { echo db_int($rows, "qty"), " ", db_int($rows, "big"), "\n"; }
```

Output:

```
3 30
```

- A column name the query does not have, or reading before `db_next`, panics. Use `AS name` for computed columns.

## db_float

```php
db_float(rows $rows, string $column): float
```

A numeric column of the current row (NULL gives 0.0).

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name, price) VALUES (?, ?)", ["cake", "89.5"]);
$rows = db_query($db, "SELECT price FROM items", []);
while (db_next($rows)) { echo db_float($rows, "price"), "\n"; }
```

Output:

```
89.5
```

## db_string

```php
db_string(rows $rows, string $column): string
```

A column of the current row as text (NULL gives `""`).

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name, qty) VALUES (?, ?)", ["ชาเย็น", "1"]);
$rows = db_query($db, "SELECT name, qty FROM items", []);
while (db_next($rows)) { echo db_string($rows, "name"), " ", db_string($rows, "qty"), "\n"; }
```

Output:

```
ชาเย็น 1
```

## db_is_null

```php
db_is_null(rows $rows, string $column): bool
```

Whether a column of the current row is NULL.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name) VALUES (?)", ["tea"]);
$rows = db_query($db, "SELECT name, qty FROM items", []);
while (db_next($rows)) { echo db_is_null($rows, "qty") ? "qty is NULL" : "qty set", "\n"; }
```

Output:

```
qty is NULL
```

- Pin has no `null` yet, so check this before trusting a 0 or `""` from a nullable column.

## db_json

```php
db_json(db $db, string $sql, list $params): string
```

Run a SELECT and get all rows as a JSON array of objects.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name, qty, price) VALUES (?, ?, ?)", ["tea", "2", "40"]);
db_exec($db, "INSERT INTO items (name) VALUES (?)", ["cake \"special\""]);
echo db_json($db, "SELECT id, name, qty, price FROM items ORDER BY id", []), "\n";
```

Output:

```
[{"id":1,"name":"tea","qty":2,"price":40.0},{"id":2,"name":"cake \"special\"","qty":null,"price":null}]
```

- Column names become keys; INTEGER, REAL, TEXT and NULL become JSON numbers, strings and `null`.
- The easiest way to answer an API request with query results — no loop, no string building.

## db_last_id

```php
db_last_id(db $db): int
```

The id of the last row inserted on this connection.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name) VALUES (?)", ["tea"]);
db_exec($db, "INSERT INTO items (name) VALUES (?)", ["cake"]);
echo db_last_id($db), "\n";
```

Output:

```
2
```

## db_error

```php
db_error(db $db): string
```

Why the last `db_exec` returned -1, or `""`.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, qty INTEGER, price REAL)", []);
db_exec($db, "INSERT INTO items (name) VALUES (?)", ["tea"]);
if (db_exec($db, "INSERT INTO items (name) VALUES (?)", ["tea"]) < 0) { echo "refused: ", db_error($db), "\n"; }
```

Output:

```
refused: UNIQUE constraint failed: items.name
```
