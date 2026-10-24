# 8. A web API

[Learn Pin](README.md) · previous: [7. Ownership](07-ownership.md) · next: [9. Errors and panics](09-errors-and-panics.md)

A Pin program can be a complete HTTP server: no web server, no PHP-FPM, one native file.

> The server is a preview: no TLS, no request headers and no timeouts yet. Use it locally; do not expose
> it to the internet.

## The smallest server

```php
function handle(string $method, string $path, string $body): string {
    return "{\"hello\":\"world\"}";
}
serve(8080, "handle");
```

Run it with `pin server.pn`, then in another terminal:

```bash
curl localhost:8080/anything
# {"hello":"world"}
```

Every request calls `handle` with the method (`"GET"`, `"POST"`, ...), the path including any query
string, and the body. Whatever it returns is the response body, sent as `application/json`. The handler must
have exactly this signature. One thread runs per CPU core; handlers cannot share variables (there are no
globals), so they need no locks.

## Test the handler without a server

`handle` is a normal function. Calling it directly is the quickest way to try your API — this is how every
example below is checked:

```php
function handle(string $method, string $path, string $body): string {
    if ($path == "/health") { return "{\"ok\":true}"; }
    http_status(404);
    return "{\"error\":\"not found\"}";
}
echo handle("GET", "/health", ""), "\n";
echo handle("GET", "/nope", ""), "\n";
```

Output:

```text
{"ok":true}
{"error":"not found"}
```

`http_status(404)` sets the status code of the current response (200 if you never call it).

## Routing and query strings

`url_path` drops the `?query`; `query_param` reads one value from it, decoded.

```php
function handle(string $method, string $path, string $body): string {
    $route = url_path($path);
    if ($method == "GET" && $route == "/hello") {
        $name = query_param($path, "name");
        if ($name == "") { $name = "stranger"; }
        return json_encode(["message" => "hello " . $name]);
    }
    http_status(404);
    return json_encode(["error" => "not found"]);
}
echo handle("GET", "/hello?name=Mint", ""), "\n";
echo handle("GET", "/hello", ""), "\n";
echo handle("GET", "/hello?name=%E0%B8%A1%E0%B8%B4%E0%B9%89%E0%B8%99%E0%B8%97%E0%B9%8C", ""), "\n";
```

Output:

```text
{"message":"hello Mint"}
{"message":"hello stranger"}
{"message":"hello มิ้นท์"}
```

Path parameters (`/users/42`) are plain string work:

```php
function user_id(string $route): int {
    return intval(substr($route, strlen("/users/")));
}
echo user_id("/users/42"), "\n";
```

Output:

```text
42
```

## Reading a JSON body

`json_has`, `json_string`, `json_int`, `json_float` and `json_bool` read one top-level key of a JSON object.
They never fail: a missing key, a wrong type or broken JSON gives the default (`""`, `0`, `0.0`, `false`).

```php
function create_order(string $body): string {
    if (!json_has($body, "item")) {
        http_status(400);
        return json_encode(["error" => "item is required"]);
    }
    $item = json_string($body, "item");
    $qty = json_int($body, "qty");
    if ($qty < 1 || $qty > 20) {
        http_status(400);
        return json_encode(["error" => "qty must be 1 to 20"]);
    }
    http_status(201);
    return "{\"item\":" . json_encode($item) . ",\"qty\":" . $qty . "}";
}
echo create_order("{\"item\": \"tea\", \"qty\": 2}"), "\n";
echo create_order("{\"qty\": 2}"), "\n";
echo create_order("{\"item\": \"tea\", \"qty\": 99999999999999999999}"), "\n";
echo create_order("not json at all"), "\n";
```

Output:

```text
{"item":"tea","qty":2}
{"error":"item is required"}
{"error":"qty must be 1 to 20"}
{"error":"item is required"}
```

A number too big for an int becomes `PHP_INT_MAX`, so the range check answers 400. **Always range-check
numbers from a request.**

Two things to notice: a map holds one value type, so a response that mixes text and numbers is built as a
string, with `json_encode()` quoting the text; and form posts (`a=1&b=2`) work the same way with
`form_param($body, "a")`.

## A complete API

```php
function prices(): map<string,int> {
    return ["coffee" => 55, "tea" => 40, "cake" => 89];
}

function quote(string $item, int $qty): string {
    $p = prices();
    if (!isset($p[$item])) { http_status(404); return "{\"error\":\"no such item\"}"; }
    if ($qty < 1 || $qty > 20) { http_status(400); return "{\"error\":\"qty must be 1 to 20\"}"; }
    return "{\"item\":" . json_encode($item) . ",\"total\":" . ($p[$item] * $qty) . "}";
}

function handle(string $method, string $path, string $body): string {
    $route = url_path($path);
    if ($method == "GET" && $route == "/menu") { return json_encode(prices()); }
    if ($method == "GET" && $route == "/quote") {
        return quote(query_param($path, "item"), intval(query_param($path, "qty")));
    }
    if ($method == "POST" && $route == "/quote") {
        return quote(json_string($body, "item"), json_int($body, "qty"));
    }
    http_status(404);
    return "{\"error\":\"not found\"}";
}

echo handle("GET", "/menu", ""), "\n";
echo handle("GET", "/quote?item=cake&qty=3", ""), "\n";
echo handle("POST", "/quote", "{\"item\":\"tea\",\"qty\":2}"), "\n";
echo handle("GET", "/quote?item=pizza&qty=1", ""), "\n";
```

Output:

```text
{"coffee":55,"tea":40,"cake":89}
{"item":"cake","total":267}
{"item":"tea","total":80}
{"error":"no such item"}
```

To serve it for real, replace the `echo` lines with `serve(8080, "handle");` and:

```bash
pin shop.pn
curl localhost:8080/menu
curl 'localhost:8080/quote?item=cake&qty=3'
curl -X POST -d '{"item":"tea","qty":2}' localhost:8080/quote
```

## When a handler fails

If something in a handler panics — a missing map key, an index out of range — that one request gets
`500 {"error":"Internal Server Error"}`, everything it allocated is freed, the panic message is printed on
the server's terminal, and the server carries on with the next request. The client never sees the
details.

## Try it

Add `GET /menu/cheap?max=50` that returns only the items costing at most `max` (default 50) as JSON.

<details><summary>One answer</summary>

```php
function prices(): map<string,int> {
    return ["coffee" => 55, "tea" => 40, "cake" => 89];
}
function handle(string $method, string $path, string $body): string {
    if (url_path($path) == "/menu/cheap") {
        $max = query_has($path, "max") ? intval(query_param($path, "max")) : 50;
        map<string,int> $out = [];
        foreach (prices() as $item => $p) {
            if ($p <= $max) { $out[$item] = $p; }
        }
        return json_encode($out);
    }
    http_status(404);
    return "{\"error\":\"not found\"}";
}
echo handle("GET", "/menu/cheap", ""), " ", handle("GET", "/menu/cheap?max=60", ""), "\n";
```

Output:

```text
{"tea":40} {"coffee":55,"tea":40}
```

</details>
