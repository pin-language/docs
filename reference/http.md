# HTTP

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`serve`](#serve) | Run an HTTP/1.1 server; never returns. |
| [`http_status`](#http_status) | Set the status code of the current response (default 200). |
| [`url_path`](#url_path) | The request path without its query string. |
| [`query_param`](#query_param) | One value from the query string, decoded, or `""`. |
| [`query_has`](#query_has) | Whether the query string has `$key`, even with an empty value. |
| [`form_param`](#form_param) | One value from a form body (`a=1&b=2`), decoded, or `""`. |
| [`form_has`](#form_has) | Whether a form body has `$key`. |

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
