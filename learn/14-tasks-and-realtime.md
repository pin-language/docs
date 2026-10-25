# 14. Tasks and real time

[Learn Pin](README.md) · previous: [13. Classes](13-classes.md)

A program often waits: for another server, for a program it started, for a message. Pin can do other work
while it waits. `go` starts a **task**, a function running alongside the rest of the program, and `await`
collects its result.

## go and await

```php
function lookup(int $id): string {
    sleep_ms(100);                  // pretend this is a slow server
    return "user$id";
}

$a = go lookup(1);
$b = go lookup(2);
$c = go lookup(3);
echo await $a, " ", await $b, " ", await $c, "\n";
```

Output:

```text
user1 user2 user3
```

The three lookups wait at the same time, so the whole program takes about 100 ms, not 300.

- `sleep_ms()` counts milliseconds, not seconds like PHP's `sleep()`.
- While one task waits, the other tasks keep running, and so do other requests in a server.

A task that is never awaited does not compile. Pin has no "fire and forget": every task belongs to the
function that started it, so its errors cannot be lost.

<!-- check: error -->
```php
function save(int $n): int { sleep_ms(1); return $n; }

function work(): int {
    $t = go save(1);
    return 0;
}
```

Error:

```text
example.pn:5: error: the task in $t (started on line 4) is not awaited when work() returns here. Add await $t before returning
```

## Many tasks, a time limit, errors

```php
function price(int $id): int throws {
    sleep_ms(10 * $id);
    if ($id == 4) { throw error(404, "no product 4"); }
    return $id * 100;
}

list<Task<int>> $ts = [];
foreach ([1, 2, 3] as $id) { $ts[] = go price($id); }
echo json_encode(try await_all($ts)), "\n";

$t = go price(4);
echo try await $t catch ($e) { -$e->code; }, "\n";

$slow = go price(30);
echo try await_timeout($slow, 50) catch ($e) { $e->code; }, "\n";
```

Output:

```text
[100,200,300]
-404
504
```

- `await_all()` waits for a whole list of tasks and returns their results in order.
- When the task's function is declared `throws`, `await` needs `try`, as every call that can fail does.
- `await_timeout()` gives up after the time limit. It cancels the task, which stops at its next wait, and
  fails with code 504.

## Tasks borrow; they do not copy

A task reads its arguments where they are, with no copy. Until it is awaited, nobody may change them:

<!-- check: error -->
```php
function total(list<int> $xs): int { sleep_ms(1); return count($xs); }

$xs = [1, 2, 3];
$t = go total($xs);
$xs[] = 4;
echo await $t;
```

Error:

```text
example.pn:5: error: cannot change $xs here: the task in $t (started on line 4) reads it until it is awaited on line 6. Change it after the await, or give the task its own copy()
```

All the tasks of a thread take turns on that thread, so two tasks never touch the same data at the same time.
Data races cannot happen.

## Requests talking to each other: the Hub

Requests share no variables. The **Hub** carries messages between them: one request publishes to a topic,
and any request subscribed to that topic receives the message, even one running on another thread.

```php
function producer(): void {
    for ($i = 1; $i <= 3; $i++) {
        sleep_ms(10);
        hub_publish("news", "story $i");
    }
}

$inbox = hub_subscribe("news");
$p = go producer();
for ($i = 0; $i < 3; $i++) {
    echo try hub_next($inbox, 1000), "\n";
}
await $p;
echo try hub_next($inbox, 50) catch ($e) { "nothing more (" . $e->code . ")"; }, "\n";
```

Output:

```text
story 1
story 2
story 3
nothing more (504)
```

`hub_next()` always takes a time limit, so nothing waits forever. Each topic keeps its last 100 messages,
and `hub_resume($topic, $lastId)` gives a reader that comes back what it missed.

## A real-time server

This is the "board" from the PACT idea. Agent A sends a message, and agent B, who is waiting, gets it at
once. B does not have to keep asking.

<!-- check: skip -->
```php
function handle(string $method, string $path, string $body): string throws {
    $route = url_path($path);
    $agent = query_param($path, "agent");
    if ($method == "POST" && $route == "/send") {
        hub_publish("inbox:" . query_param($path, "to"), $body);
        return "{\"ok\":true}";
    }
    if ($route == "/events") {                       // a stream that stays open (Server-Sent Events)
        $inbox = hub_resume("inbox:$agent", intval(request_header("Last-Event-ID")));
        try sse_start();
        while (true) {
            $msg = try hub_next($inbox, 25000) catch ($e) {
                if ($e->code != 504) { return ""; }  // the client left
                try sse_comment("ping");             // keeps the connection alive
                continue;
            };
            try sse_send_id(hub_last_id($inbox), $msg);
        }
    }
    throw error(404, "no route $route");
}
serve(8080, "handle");
```

A waiting stream costs a few kilobytes and no thread, so thousands of agents can stay connected. When one
disconnects, its request ends and its subscription closes by itself.

## The agent's side: a runner

An AI agent does not run all the time. A small Pin program, the **runner**, keeps the stream open for it
and starts the agent when a message arrives:

<!-- check: skip -->
```php
$last = 0;
while (true) {
    $s = try http_stream("http://board.local:8080/events?agent=b", [], $last, 5000) catch ($e) {
        sleep_ms(2000);                              // the board is down: try again soon
        continue;
    };
    while (true) {
        $msg = try stream_next($s, 60000) catch ($e) { break; };   // the stream ended: reconnect
        $last = stream_last_id($s);
        echo try run("claude", ["-p", "New message on the board: $msg"], 600000) catch ($e) { $e->message; }, "\n";
    }
}
```

- `run()` starts a program **without a shell**. Each argument reaches the program exactly as written, so
  message text cannot become a command.
- `http_stream()` and `http_get()` speak `http://` only, by design. To reach an https server, run a small
  proxy on the same machine (Caddy, see the [language guide](../language.md#http-server)) and call it on
  `http://127.0.0.1:...`. The proxy opens the https connection.

## Try it

Write a function `fastest(list<int> $delays): int` that starts one task per delay (each sleeps that many
milliseconds and returns its delay) and returns the sum of the results. Check that `[30, 30, 30]` takes
about 30 ms.

<details><summary>One answer</summary>

```php
function wait(int $ms): int {
    sleep_ms($ms);
    return $ms;
}

function fastest(list<int> $delays): int {
    list<Task<int>> $ts = [];
    foreach ($delays as $d) { $ts[] = go wait($d); }
    $sum = 0;
    foreach (await_all($ts) as $r) { $sum += $r; }
    return $sum;
}

echo fastest([30, 30, 30]), "\n";
```

Output:

```text
90
```

</details>
