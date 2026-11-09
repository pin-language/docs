# Numbers

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`date`](#date) | A time as text, with PHP's format letters, in UTC. |
| [`intdiv`](#intdiv) | Integer division, rounding toward zero. |
| [`round`](#round) | Round half away from zero, like PHP. |
| [`floor`](#floor) | The largest whole number not above `$x`. |
| [`ceil`](#ceil) | The smallest whole number not below `$x`. |
| [`abs`](#abs) | The value without its sign (the same type). |
| [`max`](#max) | The larger of two numbers, or the largest item of a list. |
| [`min`](#min) | The smaller of two numbers, or the smallest item of a list. |
| [`pow`](#pow) | `$base` to the power `$exp`, the same as `$base ** $exp`. |
| [`fmod`](#fmod) | The remainder of `$x / $y` for floats. |
| [`log`](#log) | Natural logarithm, or in another base. |
| [`log10`](#log10) | Base-10 logarithm. |
| [`exp`](#exp) | e to the power `$x`. |
| [`sin`](#sin) | Sine (radians). |
| [`cos`](#cos) | Cosine (radians). |
| [`tan`](#tan) | Tangent (radians). |
| [`asin`](#asin) | Arc sine, in radians. |
| [`acos`](#acos) | Arc cosine, in radians. |
| [`atan`](#atan) | Arc tangent, in radians. |
| [`atan2`](#atan2) | The angle of the point (`$x`, `$y`), in radians. |
| [`pi`](#pi) | π, the same as `M_PI`. |
| [`is_nan`](#is_nan) | Whether `$x` is NaN (not a number). |
| [`is_finite`](#is_finite) | Whether `$x` is neither infinite nor NaN. |
| [`is_infinite`](#is_infinite) | Whether `$x` is INF or -INF. |
| [`M_PI`](#m_pi) | π. |
| [`M_E`](#m_e) | e, the base of natural logarithms. |
| [`NAN`](#nan) | Not a number. |
| [`INF`](#inf) | Infinity (`-INF` for minus infinity). |
| [`PHP_FLOAT_EPSILON`](#php_float_epsilon) | The smallest float x with 1.0 + x != 1.0. |
| [`PHP_FLOAT_MAX`](#php_float_max) | The largest float. |
| [`PHP_FLOAT_MIN`](#php_float_min) | The smallest positive normal float. |
| [`sqrt`](#sqrt) | Square root. |
| [`wrapping_add`](#wrapping_add) | `$a + $b`, wrapping around on 64-bit overflow on purpose. |
| [`wrapping_sub`](#wrapping_sub) | `$a - $b` with 64-bit wrap-around. |
| [`wrapping_mul`](#wrapping_mul) | `$a * $b` with 64-bit wrap-around. |
| [`time`](#time) | The current time as seconds since 1970-01-01 00:00 UTC (Unix time). |
| [`PHP_INT_MAX`](#php_int_max) | The largest int, 9223372036854775807. |
| [`PHP_INT_MIN`](#php_int_min) | The smallest int, -9223372036854775808. |

## date

```php
date(string $format, int $timestamp = time()): string
```

A time as text, with PHP's format letters, in UTC.

```php
echo date("Y-m-d H:i:s", 0), " ", date("D, jS F Y", 1762646400), " ", date("c", 1762646400), "\n";
```

Output:

```
1970-01-01 00:00:00 Sun, 9th November 2025 2025-11-09T00:00:00+00:00
```

- Letters: `d D j l N S w z F m M n t L Y y a A g G h H i s v u e T P p O Z U c r`; `\` before a letter keeps it as it is. Anything else is copied.
- Always UTC: Pin has no time zones yet (`T` is `UTC`, `P` is `+00:00`). For an API, `date("c")` (ISO 8601) or plain `time()` numbers are the usual choice.
- **PHP:** Like `date()` with `date.timezone=UTC`.

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

## pow

```php
pow(int|float $base, int|float $exp): int|float
```

`$base` to the power `$exp`, the same as `$base ** $exp`.

```php
echo pow(2, 10), " ", 2 ** 0.5, " ", 2.0 ** -1, " ", -2 ** 2, "\n";
```

Output:

```
1024 1.4142135623731 0.5 -4
```

- Two ints give an int (wrapping past 64 bits, like `*`); an int base with a negative int exponent panics: write `2.0 ** -1`.
- `**` binds tighter than unary minus and from the right, as in PHP: `2 ** 3 ** 2` is 512.

## fmod

```php
fmod(float $x, float $y): float
```

The remainder of `$x / $y` for floats.

```php
echo fmod(10, 3), " ", fmod(-7.5, 2), "\n";
```

Output:

```
1 -1.5
```

## log

```php
log(float $x, float $base = M_E): float
```

Natural logarithm, or in another base.

```php
echo log(M_E), " ", log(8, 2), "\n";
```

Output:

```
1 3
```

## log10

```php
log10(float $x): float
```

Base-10 logarithm.

```php
echo log10(1000), "\n";
```

Output:

```
3
```

## exp

```php
exp(float $x): float
```

e to the power `$x`.

```php
echo exp(0), " ", round(exp(1), 5), "\n";
```

Output:

```
1 2.71828
```

## sin

```php
sin(float $x): float
```

Sine (radians).

```php
echo round(sin(M_PI / 2), 6), "\n";
```

Output:

```
1
```

## cos

```php
cos(float $x): float
```

Cosine (radians).

```php
echo cos(0), "\n";
```

Output:

```
1
```

## tan

```php
tan(float $x): float
```

Tangent (radians).

```php
echo round(tan(M_PI / 4), 6), "\n";
```

Output:

```
1
```

## asin

```php
asin(float $x): float
```

Arc sine, in radians.

```php
echo round(asin(1), 4), "\n";
```

Output:

```
1.5708
```

## acos

```php
acos(float $x): float
```

Arc cosine, in radians.

```php
echo acos(1), "\n";
```

Output:

```
0
```

## atan

```php
atan(float $x): float
```

Arc tangent, in radians.

```php
echo round(atan(1), 4), "\n";
```

Output:

```
0.7854
```

## atan2

```php
atan2(float $y, float $x): float
```

The angle of the point (`$x`, `$y`), in radians.

```php
echo round(atan2(1, 1), 4), "\n";
```

Output:

```
0.7854
```

## pi

```php
pi(): float
```

π, the same as `M_PI`.

```php
echo round(pi(), 5), "\n";
```

Output:

```
3.14159
```

## is_nan

```php
is_nan(float $x): bool
```

Whether `$x` is NaN (not a number).

```php
echo is_nan(NAN) ? "nan" : "number", " ", is_nan(0.5) ? "nan" : "number", "\n";
```

Output:

```
nan number
```

## is_finite

```php
is_finite(float $x): bool
```

Whether `$x` is neither infinite nor NaN.

```php
echo is_finite(1.5) ? "yes" : "no", " ", is_finite(INF) ? "yes" : "no", "\n";
```

Output:

```
yes no
```

## is_infinite

```php
is_infinite(float $x): bool
```

Whether `$x` is INF or -INF.

```php
echo is_infinite(-INF) ? "yes" : "no", "\n";
```

Output:

```
yes
```

## M_PI

```php
M_PI: float
```

π.

```php
echo round(M_PI, 5), "\n";
```

Output:

```
3.14159
```

## M_E

```php
M_E: float
```

e, the base of natural logarithms.

```php
echo round(M_E, 5), "\n";
```

Output:

```
2.71828
```

## NAN

```php
NAN: float
```

Not a number.

```php
echo is_nan(NAN) ? "nan" : "number", "\n";
```

Output:

```
nan
```

## INF

```php
INF: float
```

Infinity (`-INF` for minus infinity).

```php
echo INF > 1e308 ? "bigger" : "not", "\n";
```

Output:

```
bigger
```

## PHP_FLOAT_EPSILON

```php
PHP_FLOAT_EPSILON: float
```

The smallest float x with 1.0 + x != 1.0.

```php
echo PHP_FLOAT_EPSILON < 0.000001 ? "tiny" : "big", "\n";
```

Output:

```
tiny
```

## PHP_FLOAT_MAX

```php
PHP_FLOAT_MAX: float
```

The largest float.

```php
echo PHP_FLOAT_MAX > 1e307 ? "huge" : "small", "\n";
```

Output:

```
huge
```

## PHP_FLOAT_MIN

```php
PHP_FLOAT_MIN: float
```

The smallest positive normal float.

```php
echo PHP_FLOAT_MIN > 0 ? "positive" : "zero", "\n";
```

Output:

```
positive
```

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
