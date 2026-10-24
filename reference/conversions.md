# Conversions

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`intval`](#intval) | Convert to int. |
| [`floatval`](#floatval) | Convert to float. |
| [`strval`](#strval) | Convert to string, the way `echo` prints it. |
| [`(int)`](#int) | Cast to int: the same as `intval()`. |
| [`(float)`](#float) | Cast to float from int or string: the same as `floatval()`. |
| [`(string)`](#string) | Cast to string: the same as `strval()`. |

## intval

```php
intval(string|float|bool|int $x): int
```

Convert to int.

```php
echo intval("42"), " ", intval("  -7kg"), " ", intval("abc"), " ", intval(3.9), " ", intval("99999999999999999999"), "\n";
```

Output:

```
42 -7 0 3 9223372036854775807
```

- From a string: optional spaces and sign, then digits; anything else stops the number, so `"abc"` is 0.
- Too big for an int: `PHP_INT_MAX` / `PHP_INT_MIN`, like PHP — range-check numbers that come from requests.
- From a float: drops the fraction; NAN, INF or out-of-range floats panic.

## floatval

```php
floatval(string|int|float $x): float
```

Convert to float.

```php
echo floatval("2.5kg"), " ", floatval("-1.25e2"), " ", floatval("abc"), " ", floatval(3), "\n";
```

Output:

```
2.5 -125 0 3
```

- From a string: the leading number; `"abc"` is 0.

## strval

```php
strval(int|float|bool|string $x): string
```

Convert to string, the way `echo` prints it.

```php
echo strval(42) . "|" . strval(2.50) . "|" . strval(true) . "|" . strval(false) . "|\n";
```

Output:

```
42|2.5|1||
```

- Floats print like PHP: whole floats lose `.0` (`2.0` prints `2`). `true` is `"1"`, `false` is `""`.

## (int)

```php
(int) $x
```

Cast to int: the same as `intval()`.

```php
echo (int)"12" + (int)2.9, "\n";
```

Output:

```
14
```

## (float)

```php
(float) $x
```

Cast to float from int or string: the same as `floatval()`.

```php
echo (float)7 / 2, " ", (float)"0.5", "\n";
```

Output:

```
3.5 0.5
```

## (string)

```php
(string) $x
```

Cast to string: the same as `strval()`.

```php
echo (string)5 . "!", "\n";
```

Output:

```
5!
```

- There is no `(bool)` cast: compare instead, e.g. `$n != 0`.
