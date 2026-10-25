# HTTP

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`serve`](#serve) | Run an HTTP/1.1 server; never returns. |
| [`http_status`](#http_status) | Set the status code of the current response (default 200). |
| [`request_header`](#request_header) | The value of a request header (name matched without case), or `""` when absent. |
| [`request_has_header`](#request_has_header) | Whether the request has the header, also when its value is empty. |
| [`response_header`](#response_header) | Add a header to the response (for example `Content-Type`, `Location`, `Cache-Control`, `Set-Cookie`). |
| [`url_path`](#url_path) | The request path without its query string. |
| [`query_param`](#query_param) | One value from the query string, decoded, or `""`. |
| [`query_has`](#query_has) | Whether the query string has `$key`, even with an empty value. |
| [`form_param`](#form_param) | One value from a form body (`a=1&b=2`), decoded, or `""`. |
| [`form_has`](#form_has) | Whether a form body has `$key`. |
| [`sse_start`](#sse_start) | Turn the response into a Server-Sent Events stream (`text/event-stream`), sent as it is written. |
| [`sse_send`](#sse_send) | Send one event (`data:` lines; a newline in the text starts a new line). |
| [`sse_send_id`](#sse_send_id) | Send one event with an id; a reconnecting browser sends it back as the `Last-Event-ID` header. |
| [`sse_comment`](#sse_comment) | Send a comment line (`: text`): clients ignore it; it keeps an idle stream from being closed. |

## serve

```php
serve(int $port, "handler"): void
```

Run an HTTP/1.1 server; never returns.

```php
function handle(string $method, string $path, string $body): string {
    return json_encode(["you_asked_for" => $path]);
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

- The handler must be `function NAME(string $method, string $path, string $body): string`; its return value is the response body, sent as `application/json`.
- One thread per CPU core (`PN_THREADS=n` to change), keep-alive and pipelining. A panic in the handler answers 500 and the server keeps running.
- No TLS, no request headers and no timeouts yet: for local testing only.

## http_status

```php
http_status(int $code): void
```

Set the status code of the current response (default 200).

```php
function handle(string $method, string $path, string $body): string {
    http_status(404);
    return "{\"error\":\"not found\"}";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

## request_header

```php
request_header(string $name): string
```

The value of a request header (name matched without case), or `""` when absent.

```php
function handle(string $method, string $path, string $body): string {
    $token = request_header("Authorization");          // "Bearer abc..." or ""
    if (!str_starts_with($token, "Bearer ")) { http_status(401); return "{\"error\":\"login first\"}"; }
    return json_encode(["agent" => request_header("User-Agent")]);
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

- Spaces around the value are removed. With the same header twice, the first one is returned.
- Outside a `serve()` handler it returns `""`.
- **PHP:** Instead of `$_SERVER['HTTP_AUTHORIZATION']` or `getallheaders()['Authorization']`.

## request_has_header

```php
request_has_header(string $name): bool
```

Whether the request has the header, also when its value is empty.

```php
function handle(string $method, string $path, string $body): string {
    if (!request_has_header("X-Api-Key")) { http_status(401); return "{\"error\":\"no key\"}"; }
    return "{\"ok\":true}";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

## response_header

```php
response_header(string $name, string $value): void
```

Add a header to the response (for example `Content-Type`, `Location`, `Cache-Control`, `Set-Cookie`).

```php
function handle(string $method, string $path, string $body): string {
    if (url_path($path) == "/old") {
        http_status(301);
        response_header("Location", "/new");
        return "";
    }
    response_header("Content-Type", "text/html; charset=utf-8");   // replaces the default application/json
    response_header("Cache-Control", "no-store");
    return "<h1>hello</h1>";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

- A value with CR, LF or another control character panics (it could inject headers), so it is safe to put request data in a header.
- `Content-Length`, `Connection`, `Transfer-Encoding` and `Date` are set by the server: setting them panics.
- Call it more than once to send a header several times (`Set-Cookie`). A panic answers 500 without these headers. Outside a handler it panics.
- **PHP:** Instead of `header('Name: value')` and `setcookie()`.

## url_path

```php
url_path(string $path): string
```

The request path without its query string.

```php
echo url_path("/orders?item=tea&qty=2"), " ", url_path("/health"), "\n";
```

Output:

```
/orders /health
```

## query_param

```php
query_param(string $path, string $key): string
```

One value from the query string, decoded, or `""`.

```php
$p = "/search?q=green+tea&city=%E0%B8%81%E0%B8%97%E0%B8%A1";
echo query_param($p, "q"), "|", query_param($p, "city"), "|", query_param($p, "page"), "|\n";
```

Output:

```
green tea|กทม||
```

- `%XX` and `+` are decoded. With a repeated key, the first one wins.
- Use `query_has` to tell a missing key from an empty value.
- **PHP:** Pin's version of `$_GET[$key]`.

## query_has

```php
query_has(string $path, string $key): bool
```

Whether the query string has `$key`, even with an empty value.

```php
echo query_has("/p?limit=", "limit") ? "y" : "n", query_has("/p?debug", "debug") ? "y" : "n", query_has("/p", "limit") ? "y" : "n", "\n";
```

Output:

```
yyn
```

## form_param

```php
form_param(string $body, string $key): string
```

One value from a form body (`a=1&b=2`), decoded, or `""`.

```php
echo form_param("name=Somchai+K&qty=2", "name"), "\n";
```

Output:

```
Somchai K
```

- **PHP:** Pin's version of `$_POST[$key]` for form posts.

## form_has

```php
form_has(string $body, string $key): bool
```

Whether a form body has `$key`.

```php
echo form_has("a=1&b=", "b") ? "y" : "n", form_has("a=1", "c") ? "y" : "n", "\n";
```

Output:

```
yn
```

## sse_start

```php
sse_start(): void throws
```

Turn the response into a Server-Sent Events stream (`text/event-stream`), sent as it is written.

```php
function handle(string $method, string $path, string $body): string throws {
    $inbox = hub_subscribe("news");
    try sse_start();
    while (true) {
        $m = try hub_next($inbox, 25000) catch ($e) {
            if ($e->code != 504) { return ""; }   // the client left
            try sse_comment("ping");             // keeps proxies from closing a quiet stream
            continue;
        };
        try sse_send($m);
    }
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

- Headers set with `response_header()` before it are sent. The stream ends when the handler returns; the connection then closes.
- When the client leaves, the next `sse_*` call (or `hub_next`) fails with 499, so the handler ends and its subscription is closed.

## sse_send

```php
sse_send(string $data): void throws
```

Send one event (`data:` lines; a newline in the text starts a new line).

```php
function handle(string $method, string $path, string $body): string throws {
    try sse_start();
    try sse_send(json_encode(["n" => 1]));
    return "";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

- Fails with 499 when the client is gone, 503 when it reads too slowly (over 1 MB waiting).

## sse_send_id

```php
sse_send_id(int $id, string $data): void throws
```

Send one event with an id; a reconnecting browser sends it back as the `Last-Event-ID` header.

```php
function handle(string $method, string $path, string $body): string throws {
    try sse_start();
    $inbox = hub_resume("news", intval(request_header("Last-Event-ID")));
    $msg = try hub_next($inbox, 25000);
    try sse_send_id(hub_last_id($inbox), $msg);
    return "";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)

## sse_comment

```php
sse_comment(string $text): void throws
```

Send a comment line (`: text`): clients ignore it; it keeps an idle stream from being closed.

```php
function handle(string $method, string $path, string $body): string throws {
    try sse_start();
    try sse_comment("ping");
    return "";
}
serve(8080, "handle");
```

(Starts a server; not run in the docs.)
