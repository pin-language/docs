# Tasks (go / await)

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`sleep_ms`](#sleep_ms) | Wait this many milliseconds. Other tasks (and other requests) keep running. |
| [`await_all`](#await_all) | Wait for every task in the list and return their results, in the list's order. |
| [`await_timeout`](#await_timeout) | Like `await $t`, but give up after `$ms` milliseconds: the task is cancelled and the call fails with 504. |

## sleep_ms

```php
sleep_ms(int $ms): void
```

Wait this many milliseconds. Other tasks (and other requests) keep running.

```php
function late(string $s, int $ms): string {
    sleep_ms($ms);
    return $s;
}
$a = go late("second", 40);
$b = go late("first", 10);
echo await $b, " ", await $a, "\n";
```

Output:

```
first second
```

- Counts milliseconds, not seconds like PHP's `sleep()`: `sleep_ms(1000)` is one second.
- In a `serve()` handler it waits without holding the thread: the same thread answers other requests meanwhile.
- **PHP:** Instead of `sleep()` / `usleep()`, which block the whole process.

## await_all

```php
await_all(list<Task<T>> $tasks): list<T>
```

Wait for every task in the list and return their results, in the list's order.

```php
function square(int $n): int {
    sleep_ms(10);
    return $n * $n;
}
list<Task<int>> $ts = [];
foreach ([1, 2, 3, 4] as $n) { $ts[] = go square($n); }
echo json_encode(await_all($ts)), "\n";
```

Output:

```
[1,4,9,16]
```

- The tasks run at the same time: four 10 ms tasks take about 10 ms.
- The list is used up (moved). When the tasks' function is `throws`, write `try await_all($ts)`: the first error is the one you get, and the results of the others are freed.

## await_timeout

```php
await_timeout(Task<T> $t, int $ms): T throws
```

Like `await $t`, but give up after `$ms` milliseconds: the task is cancelled and the call fails with 504.

```php
function slow(int $ms): int {
    sleep_ms($ms);
    return $ms;
}
$quick = go slow(5);
$late = go slow(1000);
echo try await_timeout($quick, 500) catch ($e) { -1; }, " ", try await_timeout($late, 20) catch ($e) { $e->code; }, "\n";
```

Output:

```
5 504
```

- Cancelling is cooperative: the task's next wait (`sleep_ms`, `hub_next`) ends at once, so it stops soon; a long computing loop runs to its end.
- What a cancelled task returned is freed. Always needs `try` (running out of time is an error).
