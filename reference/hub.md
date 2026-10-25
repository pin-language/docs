# Hub (messages between requests)

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`hub_publish`](#hub_publish) | Send a message to everyone subscribed to the topic — also requests on other threads. |
| [`hub_subscribe`](#hub_subscribe) | Start receiving the topic's messages (those published from now on). |
| [`hub_resume`](#hub_resume) | Subscribe and also receive the kept messages with an id above `$last_id` (a reader catching up). |
| [`hub_next`](#hub_next) | The next message, waiting at most `$ms` milliseconds (other requests keep running meanwhile). |
| [`hub_last_id`](#hub_last_id) | The id of the message `hub_next` last returned. |

## hub_publish

```php
hub_publish(string $topic, string $message): void
```

Send a message to everyone subscribed to the topic — also requests on other threads.

```php
$inbox = hub_subscribe("orders");
hub_publish("orders", "{\"id\":7}");
echo try hub_next($inbox, 100) catch ($e) { "none"; }, "\n";
```

Output:

```
{"id":7}
```

- Requests share no variables; the Hub is how one request tells another (a long-poll or a stream waiting for news). The text is copied: usually `json_encode` of an object.
- Each topic keeps its last 100 messages for `hub_resume`. Messages live in memory: a restart loses them, so store what must not be lost (SQLite) and use the Hub to wake readers.

## hub_subscribe

```php
hub_subscribe(string $topic): sub
```

Start receiving the topic's messages (those published from now on).

```php
$a = hub_subscribe("t");
$b = hub_subscribe("t");
hub_publish("t", "hi");
echo try hub_next($a, 10) catch ($e) { "?"; }, " ", try hub_next($b, 10) catch ($e) { "?"; }, "\n";
```

Output:

```
hi hi
```

- The `sub` is an owned value: when it goes out of scope (or the request ends or panics) it unsubscribes.
- A reader more than 100 messages behind is dropped: its next `hub_next` fails with 507.

## hub_resume

```php
hub_resume(string $topic, int $last_id): sub
```

Subscribe and also receive the kept messages with an id above `$last_id` (a reader catching up).

```php
hub_publish("log", "one");
hub_publish("log", "two");
$r = hub_resume("log", 1);
echo try hub_next($r, 10) catch ($e) { "?"; }, "\n";
```

Output:

```
two
```

- For Server-Sent Events: `hub_resume($topic, intval(request_header("Last-Event-ID")))` gives a reconnecting client what it missed.

## hub_next

```php
hub_next(sub $s, int $ms): string throws
```

The next message, waiting at most `$ms` milliseconds (other requests keep running meanwhile).

```php
$s = hub_subscribe("quiet");
echo try hub_next($s, 20) catch ($e) { "error " . $e->code; }, "\n";
```

Output:

```
error 504
```

- Fails with 504 when nothing arrives in time, 507 when this reader fell behind, 499 when the request was cancelled (its client left). The time limit is required: nothing waits forever.

## hub_last_id

```php
hub_last_id(sub $s): int
```

The id of the message `hub_next` last returned.

```php
$s = hub_subscribe("ids");
hub_publish("ids", "a");
hub_publish("ids", "b");
$x = try hub_next($s, 10) catch ($e) { ""; };
$y = try hub_next($s, 10) catch ($e) { ""; };
echo $y, " has id ", hub_last_id($s), "\n";
```

Output:

```
b has id 2
```

- Send it as the SSE event id (`sse_send_id`) so a client can resume from it.
