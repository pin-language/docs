# 11. A database

[Learn Pin](README.md) · previous: [10. Coming from PHP](10-from-php.md)

Pin talks to SQLite: a whole database in one file, no server to install. (PostgreSQL is planned with the
same functions.) On Linux, programs that use the database need SQLite's development files:
`sudo apt install libsqlite3-dev`; macOS has them already.

## Open, create, insert

`":memory:"` is a temporary database that disappears when the program ends — handy for trying things.
Use a file name such as `"shop.db"` to keep the data.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, price INTEGER NOT NULL)", []);
db_exec($db, "INSERT INTO products (name, price) VALUES (?, ?)", ["tea", "40"]);
db_exec($db, "INSERT INTO products (name, price) VALUES (?, ?)", ["cake", "89"]);
echo "last id: ", db_last_id($db), "\n";
```

Output:

```text
last id: 2
```

Every value goes into a `?` placeholder and the list after the SQL. A list of strings is the simplest:
SQLite stores `"40"` in an INTEGER column as the number 40.

## SQL injection cannot compile

The SQL has to be written in your program. Gluing a value into it does not compile:

<!-- check: error -->
```php
$db = db_open(":memory:");
$name = "tea'; DROP TABLE products; --";
$rows = db_query($db, "SELECT * FROM products WHERE name = '" . $name . "'", []);
```

Error:

```text
example.pn:3: error: db_query(): write the SQL as a string literal in the code and pass values with ? placeholders, e.g. db_query($db, "SELECT * FROM t WHERE id = ?", [strval($id)]). SQL built from variables could let a client inject SQL
```

With a placeholder, whatever the value contains is only ever data.

## Reading rows

`db_query` gives `rows`; `db_next` moves to the next row and returns false at the end. Read columns by name.

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE products (name TEXT, price INTEGER, note TEXT)", []);
db_exec($db, "INSERT INTO products (name, price, note) VALUES (?, ?, ?)", ["tea", "40", "hot"]);
db_exec($db, "INSERT INTO products (name, price) VALUES (?, ?)", ["cake", "89"]);
$rows = db_query($db, "SELECT name, price, note FROM products WHERE price < ? ORDER BY price", ["100"]);
while (db_next($rows)) {
    $note = db_is_null($rows, "note") ? "-" : db_string($rows, "note");
    echo db_string($rows, "name"), " ", db_int($rows, "price"), " ", $note, "\n";
}
```

Output:

```text
tea 40 hot
cake 89 -
```

Pin has no `null` yet, so a NULL column reads as `0` or `""`; ask `db_is_null` when it matters.

## Straight to JSON

For an API you usually want the rows as JSON. `db_json` does the whole query in one call, with the right
JSON types:

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)", []);
db_exec($db, "INSERT INTO products (name, price) VALUES (?, ?)", ["tea", "40"]);
db_exec($db, "INSERT INTO products (name) VALUES (?)", ["ชาเย็น"]);
echo db_json($db, "SELECT id, name, price FROM products", []), "\n";
```

Output:

```text
[{"id":1,"name":"tea","price":40.0},{"id":2,"name":"ชาเย็น","price":null}]
```

## When the database says no

A constraint (UNIQUE, NOT NULL, CHECK, FOREIGN KEY) refusing a change is normal — for example, a name that
is taken. `db_exec` returns -1 and `db_error` says why:

```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE users (email TEXT UNIQUE NOT NULL)", []);
echo db_exec($db, "INSERT INTO users (email) VALUES (?)", ["a@example.com"]), "\n";
$n = db_exec($db, "INSERT INTO users (email) VALUES (?)", ["a@example.com"]);
if ($n < 0) { echo "refused: ", db_error($db), "\n"; }
```

Output:

```text
1
refused: UNIQUE constraint failed: users.email
```

Anything else — a typo in the SQL, the wrong number of values, an unknown column — is a bug in the program
and panics with SQLite's message:

<!-- check: panic -->
```php
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE t (x INTEGER)", []);
db_exec($db, "INSERT INTO t (x) VALUES (?, ?)", ["1"]);
```

Panic:

```text
panic: db_exec(): 2 values for 1 columns
```

## Connections close themselves

`$db` and `$rows` are owned values, like lists (chapter 7). When the function that owns them returns, they
close; you never call a close function. Passing `$db` to a function lends it:

```php
function count_products(db $db): int {
    $rows = db_query($db, "SELECT count(*) AS n FROM products", []);
    db_next($rows);
    return db_int($rows, "n");
}
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE products (name TEXT)", []);
db_exec($db, "INSERT INTO products (name) VALUES (?)", ["tea"]);
echo count_products($db), " product(s)\n";
```

Output:

```text
1 product(s)
```

## A JSON API with a database

In a server, open the database in each request: SQLite opens in microseconds, every request gets its own
connection, and WAL mode lets them read and write in parallel. If a handler panics, its connection and
statements are closed before the 500 goes out.

```php
function handle(string $method, string $path, string $body): string {
    $db = db_open("notes.db");
    db_exec($db, "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)", []);
    $route = url_path($path);
    if ($method == "POST" && $route == "/notes") {
        $text = json_string($body, "text");
        if ($text == "") { http_status(400); return "{\"error\":\"text is required\"}"; }
        db_exec($db, "INSERT INTO notes (text) VALUES (?)", [$text]);
        http_status(201);
        return "{\"id\":" . db_last_id($db) . "}";
    }
    if ($method == "GET" && $route == "/notes") {
        $limit = query_has($path, "limit") ? intval(query_param($path, "limit")) : 20;
        return db_json($db, "SELECT id, text FROM notes ORDER BY id DESC LIMIT ?", [$limit]);
    }
    http_status(404);
    return "{\"error\":\"not found\"}";
}
serve(8080, "handle");
```

```bash
pin notes.pn
curl -X POST -d '{"text":"buy milk"}' localhost:8080/notes
curl 'localhost:8080/notes?limit=5'
```

## Try it

Add `DELETE /notes?id=3` to the API above: delete that note and answer `{"deleted":1}`, or 404 with
`{"error":"no such note"}` when nothing was deleted (`db_exec` returns how many rows changed).

<details><summary>One answer</summary>

```php
function delete_note(db $db, string $path): string {
    $n = db_exec($db, "DELETE FROM notes WHERE id = ?", [intval(query_param($path, "id"))]);
    if ($n == 0) { http_status(404); return "{\"error\":\"no such note\"}"; }
    return "{\"deleted\":" . $n . "}";
}
$db = db_open(":memory:");
db_exec($db, "CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)", []);
db_exec($db, "INSERT INTO notes (text) VALUES (?)", ["buy milk"]);
echo delete_note($db, "/notes?id=1"), " ", delete_note($db, "/notes?id=1"), "\n";
```

Output:

```text
{"deleted":1} {"error":"no such note"}
```

</details>
