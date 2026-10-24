# Numbers

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`intdiv`](#intdiv) | Integer division, rounding toward zero. |
| [`sqrt`](#sqrt) | Square root. |
| [`wrapping_add`](#wrapping_add) | `$a + $b`, wrapping around on 64-bit overflow on purpose. |
| [`wrapping_sub`](#wrapping_sub) | `$a - $b` with 64-bit wrap-around. |
| [`wrapping_mul`](#wrapping_mul) | `$a * $b` with 64-bit wrap-around. |
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
