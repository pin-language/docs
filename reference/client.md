# Other servers and programs

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`http_get`](#http_get) | GET an http:// URL and return the body (waits without holding the thread). |
| [`http_post`](#http_post) | POST a body (sent as application/json) and return the response body. |
| [`http_stream`](#http_stream) | Open a Server-Sent Events stream (for example a board an agent listens to) and keep it open. |
| [`stream_next`](#stream_next) | The data of the next event of the stream (several `data:` lines joined with newlines; comments skipped). |
| [`stream_last_id`](#stream_last_id) | The id of the last event read (0 before any had one). |
| [`read_line`](#read_line) | One line of standard input, without its line ending. Fails with code 1 at the end of the input. |
| [`run`](#run) | Run a program and return what it printed. There is no shell: each argument reaches the program as it is. |

## http_get

```php
http_get(string $url, map<string,string> $headers, int $ms): string throws
```

GET an http:// URL and return the body (waits without holding the thread).

```php
$health = try http_get("http://127.0.0.1:8080/health", ["Authorization" => "Bearer abc"], 2000) catch ($e) {
    "down: " . $e->code;
};
echo $health, "\n";
```

(Starts a server; not run in the docs.)

- A status of 400 or more fails with that status as the code (the start of the body is in the message); 502 when the connection fails, 504 when there is no answer within `$ms`.
- Only `http://`, by design: for an https API, call a local egress proxy (Caddy) on 127.0.0.1 that opens the https connection — see design/tls.md. An https:// URL fails with 400.
- Header values with CR/LF panic. The name lookup itself still blocks the thread briefly.
- **PHP:** Instead of `file_get_contents($url)` or curl.

## http_post

```php
http_post(string $url, map<string,string> $headers, string $body, int $ms): string throws
```

POST a body (sent as application/json) and return the response body.

```php
$r = try http_post("http://127.0.0.1:8080/orders", [], json_encode(["item" => "tea"]), 2000);
echo $r, "\n";
```

(Starts a server; not run in the docs.)

- Errors as for `http_get`.

## http_stream

```php
http_stream(string $url, map<string,string> $headers, int $last_id, int $ms): stream throws
```

Open a Server-Sent Events stream (for example a board an agent listens to) and keep it open.

```php
$s = try http_stream("http://127.0.0.1:8080/events", ["X-Api-Key" => "k1"], 0, 5000);
while (true) {
    $event = try stream_next($s, 60000);
    echo "got ", $event, " (id ", stream_last_id($s), ")\n";
}
```

(Starts a server; not run in the docs.)

- With `$last_id` above 0 it sends `Last-Event-ID`, so the server can send what was missed.
- The `stream` closes when it goes out of scope. `$ms` limits connecting and the response head.

## stream_next

```php
stream_next(stream $s, int $ms): string throws
```

The data of the next event of the stream (several `data:` lines joined with newlines; comments skipped).

```php
$s = try http_stream("http://127.0.0.1:8080/events", [], 0, 5000);
$e1 = try stream_next($s, 30000) catch ($e) { "none (" . $e->code . ")"; };
echo $e1, "\n";
```

(Starts a server; not run in the docs.)

- 504 when no event comes within `$ms` (the stream stays usable); 502 when the server ended the stream: reconnect with `http_stream($url, $headers, stream_last_id($s), $ms)`.

## stream_last_id

```php
stream_last_id(stream $s): int
```

The id of the last event read (0 before any had one).

```php
$s = try http_stream("http://127.0.0.1:8080/events", [], 0, 5000);
$e1 = try stream_next($s, 30000);
echo stream_last_id($s), "\n";
```

(Starts a server; not run in the docs.)

## read_line

```php
read_line(): string throws
```

One line of standard input, without its line ending. Fails with code 1 at the end of the input.

```php
while (true) {
    $line = try read_line() catch ($e) { break; };    // the input ended
    echo strtoupper($line), "\n";
}
```

(Starts a server; not run in the docs.)

- What was echoed so far is flushed before it waits, so a program answering line by line (MCP over stdio) is never stuck with its answer in a buffer.
- Waiting does not hold the thread: other tasks keep running.
- **PHP:** Instead of `fgets(STDIN)`.

## run

```php
run(string $program, list<string> $args, int $ms): string throws
```

Run a program and return what it printed. There is no shell: each argument reaches the program as it is.

```php
echo try run("echo", ["hello", "world; rm -rf /"], 2000);
echo try run("sh", ["-c", "exit 3"], 2000) catch ($e) { "exit code " . $e->code; }, "\n";
```

Output:

```
hello world; rm -rf /
exit code 3
```

- Arguments are never interpreted by a shell, so text from a request cannot inject commands. Write `run("sh", ["-c", ...])` only with text you wrote yourself.
- A non-zero exit fails with the exit code as the error code and the start of stderr as the message; 127 when the program cannot be started; 504 when it runs longer than `$ms` (it is killed).
- The program reads nothing on stdin; output above 64 MB is cut.
- **PHP:** Instead of `exec()` / `shell_exec()` / `proc_open()`, which go through a shell.
