# Numbers

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`intdiv`](#intdiv) | Integer division, rounding toward zero. |
| [`round`](#round) | Round half away from zero, like PHP. |
| [`floor`](#floor) | The largest whole number not above `$x`. |
| [`ceil`](#ceil) | The smallest whole number not below `$x`. |
| [`abs`](#abs) | The value without its sign (the same type). |
| [`max`](#max) | The larger of two numbers, or the largest item of a list. |
| [`min`](#min) | The smaller of two numbers, or the smallest item of a list. |
| [`sqrt`](#sqrt) | Square root. |
| [`wrapping_add`](#wrapping_add) | `$a + $b`, wrapping around on 64-bit overflow on purpose. |
| [`wrapping_sub`](#wrapping_sub) | `$a - $b` with 64-bit wrap-around. |
| [`wrapping_mul`](#wrapping_mul) | `$a * $b` with 64-bit wrap-around. |
| [`time`](#time) | The current time as seconds since 1970-01-01 00:00 UTC (Unix time). |
| [`PHP_INT_MAX`](#php_int_max) | The largest int, 9223372036854775807. |
| [`PHP_INT_MIN`](#php_int_min) | The smallest int, -9223372036854775808. |

## intdiv

```php
intdiv(int $a, int $b): int
```

Integer division, rounding toward zero.

```php
echo intdiv(7, 2), " ", intdiv(-7, 2), "\n";
```

Output:

```
3 -3
```

- `/` always gives a float, like PHP; use `intdiv()` for list indexes and counts.
- Division by zero panics; `intdiv(PHP_INT_MIN, -1)` panics (there is no int answer).

## round

```php
round(float $x, int $digits = 0): float
```

Round half away from zero, like PHP.

```php
echo round(2.5), " ", round(-2.5), " ", round(1.955, 2), " ", round(1234.5, -2), "\n";
```

Output:

```
3 -3 1.96 1200
```

- `round(1.955, 2)` is 1.96 as in PHP, though the stored double is a little below 1.955.
- The result is a float; `(int)round($x)` for an int.

## floor

```php
floor(float $x): float
```

The largest whole number not above `$x`.

```php
echo floor(2.7), " ", floor(-2.1), "\n";
```

Output:

```
2 -3
```

## ceil

```php
ceil(float $x): float
```

The smallest whole number not below `$x`.

```php
echo ceil(2.1), " ", ceil(-2.7), "\n";
```

Output:

```
3 -2
```

## abs

```php
abs(int|float $x): int|float
```

The value without its sign (the same type).

```php
echo abs(-7), " ", abs(-2.5), "\n";
```

Output:

```
7 2.5
```

- `abs(PHP_INT_MIN)` wraps to itself, like `-`.

## max

```php
max(int|float $a, int|float $b): int|float  /  max(list<int|float> $xs)
```

The larger of two numbers, or the largest item of a list.

```php
echo max(3, 9), " ", max(2, 2.5), " ", max([4, 11, 7]), "\n";
```

Output:

```
9 2.5 11
```

- An int and a float give a float. `max([])` panics (PHP throws).
- **PHP:** Numbers only (no strings, no more than two values).

## min

```php
min(int|float $a, int|float $b): int|float  /  min(list<int|float> $xs)
```

The smaller of two numbers, or the smallest item of a list.

```php
echo min(3, 9), " ", min([4.5, -1.0]), "\n";
```

Output:

```
3 -1
```

- `min([])` panics (PHP throws).

## sqrt

```php
sqrt(int|float $x): float
```

Square root.

```php
echo sqrt(16), " ", sqrt(2.0), "\n";
```

Output:

```
4 1.4142135623731
```

- `sqrt` of a negative number gives NAN.

## wrapping_add

```php
wrapping_add(int $a, int $b): int
```

`$a + $b`, wrapping around on 64-bit overflow on purpose.

```php
echo wrapping_add(PHP_INT_MAX, 1) == PHP_INT_MIN ? "wrapped" : "no", "\n";
```

Output:

```
wrapped
```

- Plain `+ - *` also wrap today, but only these functions promise it: use them in hashes and checksums so the code stays correct when overflow checks are added.

## wrapping_sub

```php
wrapping_sub(int $a, int $b): int
```

`$a - $b` with 64-bit wrap-around.

```php
echo wrapping_sub(PHP_INT_MIN, 1) == PHP_INT_MAX ? "wrapped" : "no", "\n";
```

Output:

```
wrapped
```

## wrapping_mul

```php
wrapping_mul(int $a, int $b): int
```

`$a * $b` with 64-bit wrap-around.

```php
$h = 0;
foreach ([104, 105] as $c) { $h = wrapping_mul(wrapping_add($h, $c), 1099511628211); }
echo $h, "\n";
```

Output:

```
99599260821814035
```

## time

```php
time(): int
```

The current time as seconds since 1970-01-01 00:00 UTC (Unix time).

```php
$expires = time() + 3600;               // one hour from now
echo $expires > time() ? "valid\n" : "expired\n";
```

Output:

```
valid
```

- The system's wall clock: it moves when the clock is set, so use it for expiry times and timestamps, not to measure how long something took.
- Keep times as Unix seconds in the database (`INTEGER` / `BIGINT`): the same on SQLite and PostgreSQL.
- **PHP:** `time()`. No `date()` / `microtime()` yet.

## PHP_INT_MAX

```php
PHP_INT_MAX: int
```

The largest int, 9223372036854775807.

```php
echo PHP_INT_MAX, "\n";
```

Output:

```
9223372036854775807
```

## PHP_INT_MIN

```php
PHP_INT_MIN: int
```

The smallest int, -9223372036854775808.

```php
echo PHP_INT_MIN, "\n";
```

Output:

```
-9223372036854775808
```
