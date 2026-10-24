# Lists and maps

Part of the [Pin built-in reference](README.md). Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); every example below is compiled and run by its test suite, and the output shown is the real output.

| | |
|---|---|
| [`count`](#count) | Number of items in a list or entries in a map. |
| [`fill`](#fill) | A new list with `$n` copies of `$value`. |
| [`copy`](#copy) | An independent copy you own. |
| [`sort`](#sort) | Sort a list variable in place, smallest first. |
| [`rsort`](#rsort) | Sort a list variable in place, largest first. |
| [`isset`](#isset) | Whether a list index is in range or a map key exists. |
| [`array_key_exists`](#array_key_exists) | Same as `isset($m[$key])`. |
| [`unset`](#unset) | Remove a map entry (nothing happens if it is missing). |

## count

```php
count(list|map $xs): int
```

Number of items in a list or entries in a map.

```php
echo count([1, 2, 3]), " ", count(["a" => 1]), "\n";
```

Output:

```
3 1
```

## fill

```php
fill(int $n, int|float|bool|string $value): list
```

A new list with `$n` copies of `$value`.

```php
$flags = fill(3, false);
$flags[1] = true;
echo json_encode($flags), " ", json_encode(fill(2, "x")), "\n";
```

Output:

```
[false,true,false] ["x","x"]
```

- A negative or impossibly large `$n` panics.
- **PHP:** Pin's version of `array_fill(0, $n, $value)`.

## copy

```php
copy(list|map|string $x): same type
```

An independent copy you own.

```php
$a = [1, 2];
$b = copy($a);
$b[] = 3;
echo count($a), " ", count($b), "\n";
```

Output:

```
2 3
```

- Lists and maps move on `$b = $a`; use `copy()` when you need two of them.
- A function parameter is read-only; `copy()` it before changing it.

## sort

```php
sort(list $xs): void
```

Sort a list variable in place, smallest first.

```php
$xs = [3, 1, 2];
sort($xs);
$names = ["bob", "Alice", "carol"];
sort($names);
echo json_encode($xs), " ", json_encode($names), "\n";
```

Output:

```
[1,2,3] ["Alice","bob","carol"]
```

- Works on lists of int, float, bool and string; strings sort by bytes, so upper case comes before lower case.
- The argument must be a list variable you own (not a parameter, not an expression), and not one a `foreach` is walking.
- **PHP:** There are no sort flags or custom comparisons (`usort`) yet.

## rsort

```php
rsort(list $xs): void
```

Sort a list variable in place, largest first.

```php
$xs = [3, 1, 2];
rsort($xs);
echo json_encode($xs), "\n";
```

Output:

```
[3,2,1]
```

- Same rules as `sort()`.

## isset

```php
isset($list[$i] | $map[$key]): bool
```

Whether a list index is in range or a map key exists.

```php
$m = ["tea" => 40];
$xs = [10, 20];
echo isset($m["tea"]) ? "y" : "n", isset($m["cake"]) ? "y" : "n", isset($xs[1]) ? "y" : "n", isset($xs[5]) ? "y" : "n", "\n";
```

Output:

```
ynyn
```

- Use it (or `??`) before reading a key that may be missing: reading a missing map key panics.
- **PHP:** Works only on one list item or map entry; there is no `null`, so there is no `isset($x)` for a plain variable.

## array_key_exists

```php
array_key_exists(key, map|list $m): bool
```

Same as `isset($m[$key])`.

```php
$m = ["a" => 1];
echo array_key_exists("a", $m) ? "yes" : "no", "\n";
```

Output:

```
yes
```

- The container must be a variable or a function result, not a literal.

## unset

```php
unset($map[$key]): void
```

Remove a map entry (nothing happens if it is missing).

```php
$m = ["a" => 1, "b" => 2];
unset($m["a"]);
unset($m["zzz"]);
echo json_encode($m), "\n";
```

Output:

```
{"b":2}
```

- Maps only. To drop items from a list, build a new list without them.
- Not allowed while a `foreach` walks the map.
