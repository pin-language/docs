# Errors

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`error`](#error) | A new error, to throw from a function declared `throws`. |

## error

```php
error(int $code, string $message): Error
```

A new error, to throw from a function declared `throws`.

```php
function findUser(int $id): string throws {
    if ($id <= 0) { throw error(400, "bad id $id"); }
    return "user$id";
}
echo try findUser(7) catch ($e) { "?"; }, "\n";
echo try findUser(-1) catch ($e) { "failed with " . $e->code . ": " . $e->message; }, "\n";
```

Output:

```
user7
failed with 400: bad id -1
```

- An `Error` has two public properties, `$e->code` and `$e->message`; `json_encode($e)` gives both.
- A function that can fail is declared `: T throws`; every call to it needs `try` (pass the error on) or `try ... catch ($e) { ... }` (handle it). An error escaping the top level prints `error: ... (code N)` and exits 1.
- An error leaving a `serve()` handler answers its code if it is 400–599 (else 500), with the standard status text as the body; the message goes to the log only.
- **PHP:** Instead of `throw new InvalidArgumentException(...)`. Pin has one error type, and errors are values returned next to the result, not exceptions that unwind the stack.
